"""
Flask web application for the Open FAIR Monte Carlo Calculator.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify
import numpy as np

from fair_monte_carlo.models.fair_model import FAIRModel
from fair_monte_carlo.simulation.monte_carlo import MonteCarloSimulation
from fair_monte_carlo.simulation.vulnerability import calculate_vulnerability_vectorized
from fair_monte_carlo.distributions import (
    PERTDistribution,
    TriangularDistribution,
    LogNormalDistribution,
    ConstantDistribution,
)

from webapp.database import db, init_db
from webapp.models import Scenario, SimulationResult

app = Flask(__name__)


def parse_distribution(dist_data: dict):
    """Parse distribution from form data."""
    dist_type = dist_data.get("type", "constant")

    if dist_type == "triangular":
        return TriangularDistribution(
            float(dist_data["min"]),
            float(dist_data["likely"]),
            float(dist_data["max"])
        )
    elif dist_type == "pert":
        return PERTDistribution(
            float(dist_data["min"]),
            float(dist_data["likely"]),
            float(dist_data["max"])
        )
    elif dist_type == "lognormal":
        return LogNormalDistribution(
            low=float(dist_data["low"]),
            high=float(dist_data["high"])
        )
    elif dist_type == "constant":
        return ConstantDistribution(float(dist_data["value"]))
    else:
        raise ValueError(f"Unknown distribution type: {dist_type}")


@app.route("/")
def index():
    """Render the main calculator page."""
    return render_template("index.html")


@app.route("/api/simulate", methods=["POST"])
def simulate():
    """Run a Monte Carlo simulation and return results."""
    try:
        data = request.json

        # Build the FAIR model
        model = FAIRModel(name=data.get("name", "Risk Scenario"))

        calculated_vulnerability = None

        # Handle LEF inputs
        if "lef" in data:
            # Direct LEF input
            model.lef = parse_distribution(data["lef"])
        else:
            # Derived LEF from TEF and Vulnerability

            # Handle TEF
            if "tef" in data:
                # Direct TEF input
                model.tef = parse_distribution(data["tef"])
            elif "contact_frequency" in data and "probability_of_action" in data:
                # Derived TEF from CF and PoA
                model.contact_frequency = parse_distribution(data["contact_frequency"])
                model.probability_of_action = parse_distribution(data["probability_of_action"])
            else:
                raise ValueError("Must specify either TEF or (Contact Frequency + Probability of Action)")

            # Handle Vulnerability
            if "vulnerability" in data:
                # Direct vulnerability input
                model.vulnerability = parse_distribution(data["vulnerability"])
            elif "threat_capability" in data and "resistance_strength" in data:
                # Derived vulnerability from TCap and RS using 21x21 grid
                tcap = data["threat_capability"]
                rs = data["resistance_strength"]

                # Calculate vulnerability using the grid simulator
                calculated_vulnerability = calculate_vulnerability_vectorized(
                    tcap_min=float(tcap["min"]),
                    tcap_ml=float(tcap["likely"]),
                    tcap_max=float(tcap["max"]),
                    rs_min=float(rs["min"]),
                    rs_ml=float(rs["likely"]),
                    rs_max=float(rs["max"])
                )

                # Use the calculated vulnerability as a constant
                model.vulnerability = ConstantDistribution(calculated_vulnerability)
            else:
                raise ValueError("Must specify either Vulnerability or (Threat Capability + Resistance Strength)")

        # Handle Loss Magnitude inputs
        if "loss" in data:
            # Direct LM input
            model.lm = parse_distribution(data["loss"])
        elif "primary_loss" in data:
            # Derived LM from Primary + Secondary Loss
            model.primary_loss = parse_distribution(data["primary_loss"])

            # Secondary loss is optional
            if "secondary_loss_frequency" in data and "secondary_loss_magnitude" in data:
                model.secondary_loss_frequency = parse_distribution(data["secondary_loss_frequency"])
                model.secondary_loss_magnitude = parse_distribution(data["secondary_loss_magnitude"])
        else:
            raise ValueError("Must specify either Loss Magnitude or Primary Loss")

        # Run simulation
        iterations = int(data.get("iterations", 10000))
        seed = int(data.get("seed", 42))
        sim = MonteCarloSimulation(iterations=iterations, seed=seed)
        results = sim.run(model)

        # Prepare response data
        summary = results.summary()

        # Generate histogram data
        hist_counts, hist_bins = np.histogram(results.ale_samples, bins=50)

        # Generate exceedance curve data
        sorted_ale = np.sort(results.ale_samples)
        exceedance_probs = 1 - np.arange(1, len(sorted_ale) + 1) / len(sorted_ale)

        # Downsample for response
        sample_indices = np.linspace(0, len(sorted_ale) - 1, 100, dtype=int)

        response = {
            "success": True,
            "summary": {
                "mean": float(summary["ale"]["mean"]),
                "median": float(summary["ale"]["median"]),
                "std": float(summary["ale"]["std"]),
                "min": float(summary["ale"]["min"]),
                "max": float(summary["ale"]["max"]),
                "p10": float(summary["ale"]["percentile_10"]),
                "p25": float(summary["ale"]["percentile_25"]),
                "p75": float(summary["ale"]["percentile_75"]),
                "p90": float(summary["ale"]["percentile_90"]),
                "p95": float(summary["ale"]["percentile_95"]),
                "var_95": float(summary["ale"]["var_95"]),
                "cvar_95": float(summary["ale"]["cvar_95"]),
            },
            "lef": {
                "mean": float(summary["lef"]["mean"]),
                "median": float(summary["lef"]["median"]),
            },
            "lm": {
                "mean": float(summary["lm"]["mean"]),
                "median": float(summary["lm"]["median"]),
            },
            "histogram": {
                "counts": hist_counts.tolist(),
                "bins": hist_bins.tolist(),
            },
            "exceedance": {
                "values": sorted_ale[sample_indices].tolist(),
                "probabilities": (exceedance_probs[sample_indices] * 100).tolist(),
            },
            "iterations": iterations,
            "seed": seed,
        }

        # Include calculated vulnerability if it was derived from TCap/RS
        if calculated_vulnerability is not None:
            response["calculated_vulnerability"] = float(calculated_vulnerability)

        # Save result if requested
        if data.get("save_result") and data.get("scenario_id"):
            try:
                result_record = SimulationResult(
                    scenario_id=data["scenario_id"],
                    iterations=iterations,
                    seed=seed,
                    summary_stats=response["summary"],
                    histogram_data=response["histogram"],
                    exceedance_data=response["exceedance"],
                )
                db.session.add(result_record)
                db.session.commit()
                response["result_id"] = result_record.id
            except Exception as e:
                # Log but don't fail the simulation if save fails
                print(f"Warning: Failed to save result: {e}")

        return jsonify(response)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route("/api/vulnerability", methods=["POST"])
def calculate_vuln():
    """Calculate vulnerability using the 21x21 grid simulator."""
    try:
        data = request.json

        vuln = calculate_vulnerability_vectorized(
            tcap_min=float(data["tcap_min"]),
            tcap_ml=float(data["tcap_likely"]),
            tcap_max=float(data["tcap_max"]),
            rs_min=float(data["rs_min"]),
            rs_ml=float(data["rs_likely"]),
            rs_max=float(data["rs_max"])
        )

        return jsonify({
            "success": True,
            "vulnerability": float(vuln)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route("/api/compare", methods=["POST"])
def compare():
    """Compare two scenarios."""
    try:
        data = request.json

        scenarios = []
        for scenario_data in [data.get("baseline"), data.get("alternative")]:
            model = FAIRModel(name=scenario_data.get("name", "Scenario"))

            # Handle LEF
            if "lef" in scenario_data:
                model.lef = parse_distribution(scenario_data["lef"])
            elif "tef" in scenario_data:
                model.tef = parse_distribution(scenario_data["tef"])
                if "vulnerability" in scenario_data:
                    model.vulnerability = parse_distribution(scenario_data["vulnerability"])

            # Handle LM
            if "loss" in scenario_data:
                model.lm = parse_distribution(scenario_data["loss"])
            elif "primary_loss" in scenario_data:
                model.primary_loss = parse_distribution(scenario_data["primary_loss"])

            scenarios.append(model)

        # Run comparison
        iterations = int(data.get("iterations", 10000))
        sim = MonteCarloSimulation(iterations=iterations)
        comparison = sim.run_comparison(scenarios[0], scenarios[1])

        return jsonify({
            "success": True,
            "baseline_mean": float(comparison["baseline"].mean("ale")),
            "alternative_mean": float(comparison["alternative"].mean("ale")),
            "risk_reduction": float(comparison["risk_reduction"]["mean"]),
            "reduction_percent": float(comparison["relative_reduction_pct"]["mean"]),
            "prob_positive": float(comparison["risk_reduction"]["prob_positive_reduction"]),
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ==================== Scenario CRUD Endpoints ====================

@app.route("/api/scenarios", methods=["GET"])
def list_scenarios():
    """List all saved scenarios."""
    try:
        scenarios = Scenario.query.order_by(Scenario.updated_at.desc()).all()
        return jsonify({
            "success": True,
            "scenarios": [s.to_dict() for s in scenarios]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/scenarios", methods=["POST"])
def create_scenario():
    """Save a new scenario."""
    try:
        data = request.json
        scenario = Scenario(
            name=data.get("name", "Unnamed Scenario"),
            description=data.get("description"),
            lef_config=data.get("lef_config", {}),
            lm_config=data.get("lm_config", {}),
            iterations=data.get("iterations", 10000),
        )
        db.session.add(scenario)
        db.session.commit()
        return jsonify({
            "success": True,
            "scenario": scenario.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/scenarios/<int:scenario_id>", methods=["GET"])
def get_scenario(scenario_id):
    """Get a scenario by ID."""
    try:
        scenario = Scenario.query.get_or_404(scenario_id)
        return jsonify({
            "success": True,
            "scenario": scenario.to_dict()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 404


@app.route("/api/scenarios/<int:scenario_id>", methods=["PUT"])
def update_scenario(scenario_id):
    """Update a scenario."""
    try:
        scenario = Scenario.query.get_or_404(scenario_id)
        data = request.json

        if "name" in data:
            scenario.name = data["name"]
        if "description" in data:
            scenario.description = data["description"]
        if "lef_config" in data:
            scenario.lef_config = data["lef_config"]
        if "lm_config" in data:
            scenario.lm_config = data["lm_config"]
        if "iterations" in data:
            scenario.iterations = data["iterations"]

        db.session.commit()
        return jsonify({
            "success": True,
            "scenario": scenario.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/scenarios/<int:scenario_id>", methods=["DELETE"])
def delete_scenario(scenario_id):
    """Delete a scenario."""
    try:
        scenario = Scenario.query.get_or_404(scenario_id)
        db.session.delete(scenario)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


# ==================== Simulation Results Endpoints ====================

@app.route("/api/scenarios/<int:scenario_id>/results", methods=["GET"])
def get_scenario_results(scenario_id):
    """Get all simulation results for a scenario."""
    try:
        # Verify scenario exists
        Scenario.query.get_or_404(scenario_id)
        results = SimulationResult.query.filter_by(scenario_id=scenario_id)\
            .order_by(SimulationResult.executed_at.desc()).all()
        return jsonify({
            "success": True,
            "results": [r.to_dict() for r in results]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 404


@app.route("/api/results", methods=["POST"])
def save_result():
    """Save a simulation result."""
    try:
        data = request.json

        # Verify scenario exists
        Scenario.query.get_or_404(data["scenario_id"])

        result = SimulationResult(
            scenario_id=data["scenario_id"],
            iterations=data.get("iterations", 10000),
            seed=data.get("seed"),
            summary_stats=data.get("summary_stats", {}),
            histogram_data=data.get("histogram_data"),
            exceedance_data=data.get("exceedance_data"),
        )
        db.session.add(result)
        db.session.commit()
        return jsonify({
            "success": True,
            "result": result.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/results/<int:result_id>", methods=["GET"])
def get_result(result_id):
    """Get a simulation result by ID."""
    try:
        result = SimulationResult.query.get_or_404(result_id)
        return jsonify({
            "success": True,
            "result": result.to_dict()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 404


@app.route("/api/results/<int:result_id>", methods=["DELETE"])
def delete_result(result_id):
    """Delete a simulation result."""
    try:
        result = SimulationResult.query.get_or_404(result_id)
        db.session.delete(result)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000, help="Port to run on")
    args = parser.parse_args()

    # Initialize database
    init_db(app)

    app.run(debug=True, host="0.0.0.0", port=args.port)
