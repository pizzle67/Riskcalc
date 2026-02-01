"""
Flask web application for the Open FAIR Monte Carlo Calculator.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify
import numpy as np

from fair_monte_carlo import (
    RiskScenario,
    MonteCarloSimulation,
    PERTDistribution,
    LogNormalDistribution,
    ConstantDistribution,
    RiskReport,
)

app = Flask(__name__)


def parse_distribution(dist_type: str, params: dict):
    """Parse distribution from form data."""
    if dist_type == "pert":
        return PERTDistribution(
            float(params["min"]),
            float(params["likely"]),
            float(params["max"])
        )
    elif dist_type == "lognormal":
        return LogNormalDistribution(
            low=float(params["low"]),
            high=float(params["high"])
        )
    elif dist_type == "constant":
        return ConstantDistribution(float(params["value"]))
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

        # Build the scenario
        scenario = RiskScenario(data.get("name", "Risk Scenario"))

        # Parse TEF
        tef_data = data.get("tef", {})
        if tef_data.get("type") == "pert":
            scenario.with_tef(PERTDistribution(
                float(tef_data["min"]),
                float(tef_data["likely"]),
                float(tef_data["max"])
            ))
        else:
            scenario.with_tef(float(tef_data.get("value", 10)))

        # Parse Vulnerability
        vuln_data = data.get("vulnerability", {})
        if vuln_data.get("type") == "pert":
            scenario.with_vulnerability(PERTDistribution(
                float(vuln_data["min"]),
                float(vuln_data["likely"]),
                float(vuln_data["max"])
            ))
        else:
            scenario.with_vulnerability(float(vuln_data.get("value", 0.5)))

        # Parse Loss Magnitude
        loss_data = data.get("loss", {})
        if loss_data.get("type") == "pert":
            scenario.with_primary_loss(PERTDistribution(
                float(loss_data["min"]),
                float(loss_data["likely"]),
                float(loss_data["max"])
            ))
        elif loss_data.get("type") == "lognormal":
            scenario.with_primary_loss(LogNormalDistribution(
                low=float(loss_data["low"]),
                high=float(loss_data["high"])
            ))
        else:
            scenario.with_primary_loss(float(loss_data.get("value", 100000)))

        # Run simulation
        iterations = int(data.get("iterations", 10000))
        sim = MonteCarloSimulation(iterations=iterations, seed=42)
        results = sim.run(scenario.build())

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
        }

        return jsonify(response)

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
            scenario = RiskScenario(scenario_data.get("name", "Scenario"))

            # TEF
            tef = scenario_data.get("tef", {})
            if tef.get("type") == "pert":
                scenario.with_tef(PERTDistribution(
                    float(tef["min"]), float(tef["likely"]), float(tef["max"])
                ))
            else:
                scenario.with_tef(float(tef.get("value", 10)))

            # Vulnerability
            vuln = scenario_data.get("vulnerability", {})
            if vuln.get("type") == "pert":
                scenario.with_vulnerability(PERTDistribution(
                    float(vuln["min"]), float(vuln["likely"]), float(vuln["max"])
                ))
            else:
                scenario.with_vulnerability(float(vuln.get("value", 0.5)))

            # Loss
            loss = scenario_data.get("loss", {})
            if loss.get("type") == "lognormal":
                scenario.with_primary_loss(LogNormalDistribution(
                    low=float(loss["low"]), high=float(loss["high"])
                ))
            else:
                scenario.with_primary_loss(float(loss.get("value", 100000)))

            scenarios.append(scenario.build())

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


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000, help="Port to run on")
    args = parser.parse_args()
    app.run(debug=True, host="0.0.0.0", port=args.port)
