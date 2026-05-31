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

class ReverseProxied:
    """Middleware that sets SCRIPT_NAME from X-Forwarded-Prefix header,
    so url_for generates correct URLs behind Traefik PathPrefixStrip."""
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        prefix = environ.get("HTTP_X_FORWARDED_PREFIX", "")
        if prefix:
            environ["SCRIPT_NAME"] = prefix
            path_info = environ.get("PATH_INFO", "")
            if path_info.startswith(prefix):
                environ["PATH_INFO"] = path_info[len(prefix):]
        return self.app(environ, start_response)


app = Flask(__name__, template_folder='views')
app.wsgi_app = ReverseProxied(app.wsgi_app)

init_db(app)


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


@app.route("/health")
def health():
    """Health check endpoint for Nomad/Consul service monitoring."""
    return jsonify({"status": "healthy"}), 200


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

        # Generate LEF event count distribution (likelihood histogram)
        lef_int = results.lef_samples.astype(int)
        max_events = int(lef_int.max()) if len(lef_int) > 0 else 0
        event_labels = list(range(0, max_events + 1))
        event_counts_arr = np.bincount(lef_int, minlength=max_events + 1)
        event_probabilities = (event_counts_arr / iterations * 100).tolist()
        zero_event_pct = float(event_probabilities[0]) if event_probabilities else 0.0

        # Single-event view: LM distribution stats, histogram, exceedance
        lm = results.lm_samples
        lm_above_95 = lm[lm >= np.percentile(lm, 95)]
        se_summary = {
            "mean": float(np.mean(lm)),
            "median": float(np.median(lm)),
            "std": float(np.std(lm)),
            "min": float(np.min(lm)),
            "max": float(np.max(lm)),
            "p10": float(np.percentile(lm, 10)),
            "p25": float(np.percentile(lm, 25)),
            "p75": float(np.percentile(lm, 75)),
            "p90": float(np.percentile(lm, 90)),
            "p95": float(np.percentile(lm, 95)),
            "var_95": float(np.percentile(lm, 95)),
            "cvar_95": float(np.mean(lm_above_95) if len(lm_above_95) > 0 else np.percentile(lm, 95)),
        }
        se_hist_counts, se_hist_bins = np.histogram(lm, bins=50)
        sorted_lm = np.sort(lm)
        se_exceed_probs = 1 - np.arange(1, len(sorted_lm) + 1) / len(sorted_lm)
        se_sample_idx = np.linspace(0, len(sorted_lm) - 1, 100, dtype=int)

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
            "likelihood": {
                "event_labels": event_labels,
                "probabilities": event_probabilities,
                "zero_event_pct": zero_event_pct,
            },
            "single_event": {
                "event_probability": 100.0 - zero_event_pct,
                "summary": se_summary,
                "histogram": {
                    "counts": se_hist_counts.tolist(),
                    "bins": se_hist_bins.tolist(),
                },
                "exceedance": {
                    "values": sorted_lm[se_sample_idx].tolist(),
                    "probabilities": (se_exceed_probs[se_sample_idx] * 100).tolist(),
                },
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


@app.route("/api/tornado", methods=["POST"])
def tornado():
    """
    Compute Spearman rank correlation between each FAIR leaf input and ALE.

    Methodology:
      1. Sample each of the seven leaf inputs from its PERT distribution.
      2. Compute per-trial Annualized Loss Expectancy using the standard
         FAIR chain (TEF = CF * PoA; LEF derived from TEF and a continuous
         vulnerability proxy max(0, TC - RS); ALE = LEF * (PL + SLEF * SLM)).
      3. For each input, compute Spearman rank correlation against ALE.
      4. Return correlations sorted by absolute magnitude.

    The continuous vulnerability proxy is used for per-trial sensitivity
    analysis. The Open FAIR 21x21 grid produces a single scalar vulnerability
    that does not vary trial-to-trial and therefore cannot drive correlation.
    """
    try:
        from scipy.stats import spearmanr

        data = request.json
        iterations = int(data.get("iterations", 10000))
        seed = int(data.get("seed", 42))
        rng = np.random.default_rng(seed)

        def sample(key):
            return parse_distribution(data[key]).sample(iterations, rng)

        cf   = np.maximum(sample("contact_frequency"), 0)
        poa  = np.clip(sample("probability_of_action"),    0, 1)
        tc   = np.clip(sample("threat_capability"),        0, 1)
        rs   = np.clip(sample("resistance_strength"),      0, 1)
        pl   = np.maximum(sample("primary_loss"),          0)
        slef = np.clip(sample("secondary_loss_frequency"), 0, 1)
        slm  = np.maximum(sample("secondary_loss_magnitude"), 0)

        tef = cf * poa
        vuln = np.maximum(tc - rs, 0.0)
        lef = tef * vuln
        ale = lef * (pl + slef * slm)

        inputs_map = {
            "Contact Frequency":         cf,
            "Probability of Action":     poa,
            "Threat Capability":         tc,
            "Resistance Strength":       rs,
            "Primary Loss":              pl,
            "Secondary Loss Frequency":  slef,
            "Secondary Loss Magnitude":  slm,
        }

        rows = []
        for label, samples in inputs_map.items():
            try:
                rho, _p = spearmanr(samples, ale)
                if not np.isfinite(rho):
                    rho = 0.0
            except Exception:
                rho = 0.0
            rows.append({"input": label, "rho": float(rho)})

        rows.sort(key=lambda r: abs(r["rho"]), reverse=True)

        return jsonify({
            "success": True,
            "iterations": iterations,
            "seed": seed,
            "rows": rows,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/decision", methods=["POST"])
def decision():
    """
    Run a Monte Carlo decision analysis on a proposed control.

    For each trial:
      1. Sample baseline Annualized Loss Expectancy from the same chain as
         /api/tornado (continuous vulnerability proxy max(0, TC - RS)).
      2. Sample control parameters: loss reduction, implementation cost,
         ongoing operating cost, and discount rate.
      3. Draw a Bernoulli cancellation flag. On cancellation, the trial
         pays implementation cost in year 0 and recovers salvage value in
         year 1, with no benefits or further operating costs.
      4. For active trials, compute annual cashflows over the time horizon:
           - Year 0: -implementation_cost - ongoing_cost
           - Year t (t >= ramp_up): benefit_t - ongoing_cost
             where benefit_t = baseline_ale - max(residual_floor,
                                                  baseline_ale * (1 - r_t))
             and r_t = loss_reduction * (1 - decay)^(t - ramp_up)
           - Year t (t < ramp_up): -ongoing_cost
      5. Discount cashflows by the per-trial discount rate.
      6. Sum to net present value per trial.

    Returns the net present value distribution plus a tornado-style rank
    correlation of decision drivers against net present value.
    """
    try:
        from scipy.stats import spearmanr

        data = request.json
        baseline = data["baseline"]
        control = data["control"]
        iterations = int(data.get("iterations", 10000))
        seed = int(data.get("seed", 42))
        rng = np.random.default_rng(seed)

        def sample(d):
            return parse_distribution(d).sample(iterations, rng)

        cf   = np.maximum(sample(baseline["contact_frequency"]), 0)
        poa  = np.clip(sample(baseline["probability_of_action"]),    0, 1)
        tc   = np.clip(sample(baseline["threat_capability"]),        0, 1)
        rs   = np.clip(sample(baseline["resistance_strength"]),      0, 1)
        pl   = np.maximum(sample(baseline["primary_loss"]),          0)
        slef = np.clip(sample(baseline["secondary_loss_frequency"]), 0, 1)
        slm  = np.maximum(sample(baseline["secondary_loss_magnitude"]), 0)

        tef = cf * poa
        vuln = np.maximum(tc - rs, 0.0)
        lef = tef * vuln
        ale_baseline = lef * (pl + slef * slm)

        r_samples  = np.clip(sample(control["loss_reduction"]),       0, 1)
        c0_samples = np.maximum(sample(control["implementation_cost"]), 0)
        cy_samples = np.maximum(sample(control["ongoing_cost"]),        0)
        d_samples  = np.clip(sample(control["discount_rate"]),        0, 1)

        horizon = int(control.get("horizon_years", 5))
        ramp_up = int(control.get("ramp_up_year", 1))
        decay = float(control.get("efficacy_decay", 0.05))
        salvage = float(control.get("salvage_value", 0.0))
        residual_floor = float(control.get("residual_loss_floor", 0.0))
        p_cancel = float(control.get("cancellation_probability", 0.10))

        cancelled = rng.random(iterations) < p_cancel

        t = np.arange(horizon)
        discount = 1.0 / (1.0 + d_samples[:, None]) ** t[None, :]

        # Per-year benefit for active trials
        benefit_mask = (t >= ramp_up).astype(float)
        decay_factor = (1.0 - decay) ** np.maximum(0, t - ramp_up)
        effective_r = r_samples[:, None] * decay_factor[None, :] * benefit_mask[None, :]
        post_ale = np.maximum(residual_floor, ale_baseline[:, None] * (1.0 - effective_r))
        benefit = ale_baseline[:, None] - post_ale

        costs = np.zeros((iterations, horizon))
        costs[:, 0] = c0_samples
        costs += cy_samples[:, None]
        cashflow_active = benefit - costs

        cashflow_cancelled = np.zeros((iterations, horizon))
        cashflow_cancelled[:, 0] = -c0_samples
        if horizon > 1:
            cashflow_cancelled[:, 1] = salvage

        cashflow = np.where(cancelled[:, None], cashflow_cancelled, cashflow_active)
        npv = np.sum(cashflow * discount, axis=1)

        # Worst-case 5% tail uses lower quantile (since negative net present value is bad)
        p5 = float(np.percentile(npv, 5))
        npv_below_5 = npv[npv <= p5]
        summary = {
            "mean":    float(np.mean(npv)),
            "median":  float(np.median(npv)),
            "std":     float(np.std(npv)),
            "min":     float(np.min(npv)),
            "max":     float(np.max(npv)),
            "p10":     float(np.percentile(npv, 10)),
            "p25":     float(np.percentile(npv, 25)),
            "p75":     float(np.percentile(npv, 75)),
            "p90":     float(np.percentile(npv, 90)),
            "p95":     float(np.percentile(npv, 95)),
            "var_95":  p5,
            "cvar_95": float(np.mean(npv_below_5) if len(npv_below_5) > 0 else p5),
        }

        active_mask = ~cancelled
        if active_mask.any() and horizon > ramp_up:
            post_ramp_benefit = benefit[active_mask, ramp_up:]
            expected_annual_savings = float(np.mean(post_ramp_benefit))
        else:
            expected_annual_savings = 0.0

        hist_counts, hist_bins = np.histogram(npv, bins=50)
        sorted_npv = np.sort(npv)
        exceedance_probs = 1 - np.arange(1, len(sorted_npv) + 1) / len(sorted_npv)
        sample_idx = np.linspace(0, len(sorted_npv) - 1, 100, dtype=int)

        drivers = {
            "Baseline Annualized Loss Expectancy": ale_baseline,
            "Loss Reduction":                       r_samples,
            "Implementation Cost":                  c0_samples,
            "Ongoing Operating Cost":               cy_samples,
            "Discount Rate":                        d_samples,
            "Cancellation":                         cancelled.astype(float),
        }
        rows = []
        for label, samples in drivers.items():
            try:
                rho, _p = spearmanr(samples, npv)
                if not np.isfinite(rho):
                    rho = 0.0
            except Exception:
                rho = 0.0
            rows.append({"input": label, "rho": float(rho)})
        rows.sort(key=lambda r: abs(r["rho"]), reverse=True)

        return jsonify({
            "success": True,
            "summary": summary,
            "prob_positive": float(np.mean(npv > 0) * 100),
            "prob_cancelled": float(np.mean(cancelled) * 100),
            "expected_baseline_ale": float(np.mean(ale_baseline)),
            "expected_annual_savings": expected_annual_savings,
            "histogram": {
                "counts": hist_counts.tolist(),
                "bins": hist_bins.tolist(),
            },
            "exceedance": {
                "values": sorted_npv[sample_idx].tolist(),
                "probabilities": (exceedance_probs[sample_idx] * 100).tolist(),
            },
            "tornado": rows,
            "horizon_years": horizon,
            "ramp_up_year": ramp_up,
            "iterations": iterations,
            "seed": seed,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/decision-grid", methods=["POST"])
def decision_grid():
    """
    Compute three deterministic decision heatmaps over a cost x reduction
    grid for pessimistic / likely / optimistic scenarios of the other
    parameters.

    For each scenario, each cell of the grid is the expected net present
    value of a control with the given implementation cost and loss
    reduction, computed deterministically as:

        expected_npv = (1 - p_cancel) * active_npv + p_cancel * cancelled_npv

      where active_npv assumes the control runs successfully for the
      horizon and cancelled_npv pays the implementation cost in year 0
      and recovers the salvage value in year 1.

    Scenario knobs:
      Pessimistic:  baseline Annualized Loss Expectancy at 10th percentile,
                    ongoing cost at its PERT maximum, discount rate at its
                    PERT maximum.
      Likely:       baseline at 50th percentile, ongoing cost and discount
                    rate at their PERT most-likely values.
      Optimistic:   baseline at 90th percentile, ongoing cost at its PERT
                    minimum, discount rate at its PERT minimum.

    All other control parameters (cancellation probability, horizon,
    ramp-up, efficacy decay, salvage, residual loss floor) are held
    constant across scenarios.

    The cost and reduction axes auto-fit to the PERT bounds of the
    corresponding control inputs.
    """
    try:
        data = request.json
        baseline = data["baseline"]
        control = data["control"]
        iterations = int(data.get("iterations", 10000))
        seed = int(data.get("seed", 42))
        grid_size = int(data.get("grid_size", 12))
        rng = np.random.default_rng(seed)

        def sample(d):
            return parse_distribution(d).sample(iterations, rng)

        cf   = np.maximum(sample(baseline["contact_frequency"]), 0)
        poa  = np.clip(sample(baseline["probability_of_action"]),    0, 1)
        tc   = np.clip(sample(baseline["threat_capability"]),        0, 1)
        rs   = np.clip(sample(baseline["resistance_strength"]),      0, 1)
        pl   = np.maximum(sample(baseline["primary_loss"]),          0)
        slef = np.clip(sample(baseline["secondary_loss_frequency"]), 0, 1)
        slm  = np.maximum(sample(baseline["secondary_loss_magnitude"]), 0)
        tef = cf * poa
        vuln = np.maximum(tc - rs, 0.0)
        ale_baseline = (tef * vuln) * (pl + slef * slm)

        ale_p10 = float(np.percentile(ale_baseline, 10))
        ale_p50 = float(np.percentile(ale_baseline, 50))
        ale_p90 = float(np.percentile(ale_baseline, 90))

        ongoing_d = control["ongoing_cost"]
        discount_d = control["discount_rate"]
        cost_d = control["implementation_cost"]
        red_d = control["loss_reduction"]

        horizon = int(control.get("horizon_years", 5))
        ramp_up = int(control.get("ramp_up_year", 1))
        decay = float(control.get("efficacy_decay", 0.05))
        salvage = float(control.get("salvage_value", 0.0))
        residual_floor = float(control.get("residual_loss_floor", 0.0))
        p_cancel = float(control.get("cancellation_probability", 0.10))

        cost_axis = np.linspace(float(cost_d["min"]), float(cost_d["max"]), grid_size)
        red_axis  = np.linspace(float(red_d["min"]),  float(red_d["max"]),  grid_size)

        t = np.arange(horizon)
        decay_factor = (1.0 - decay) ** np.maximum(0, t - ramp_up)
        benefit_mask = (t >= ramp_up).astype(float)
        decay_yearly = decay_factor * benefit_mask

        def compute(ale, ongoing, discount):
            discount_factors = 1.0 / (1.0 + discount) ** t
            effective_r = red_axis[:, None] * decay_yearly[None, :]
            post_ale = np.maximum(residual_floor, ale * (1.0 - effective_r))
            benefit_per_year = ale - post_ale
            cashflow = benefit_per_year - ongoing
            npv_no_cost = np.sum(cashflow * discount_factors[None, :], axis=1)
            npv_active = npv_no_cost[:, None] - cost_axis[None, :]
            if horizon > 1:
                npv_cancelled_per_cost = -cost_axis + salvage * discount_factors[1]
            else:
                npv_cancelled_per_cost = -cost_axis
            npv_cancelled = np.tile(npv_cancelled_per_cost, (grid_size, 1))
            return (1 - p_cancel) * npv_active + p_cancel * npv_cancelled

        grid_pess = compute(ale_p10, float(ongoing_d["max"]),    float(discount_d["max"]))
        grid_lkly = compute(ale_p50, float(ongoing_d["likely"]), float(discount_d["likely"]))
        grid_opti = compute(ale_p90, float(ongoing_d["min"]),    float(discount_d["min"]))

        return jsonify({
            "success": True,
            "cost_axis":      cost_axis.tolist(),
            "reduction_axis": red_axis.tolist(),
            "pessimistic": {
                "baseline_ale":  ale_p10,
                "ongoing_cost":  float(ongoing_d["max"]),
                "discount_rate": float(discount_d["max"]),
                "grid":          grid_pess.tolist(),
            },
            "likely": {
                "baseline_ale":  ale_p50,
                "ongoing_cost":  float(ongoing_d["likely"]),
                "discount_rate": float(discount_d["likely"]),
                "grid":          grid_lkly.tolist(),
            },
            "optimistic": {
                "baseline_ale":  ale_p90,
                "ongoing_cost":  float(ongoing_d["min"]),
                "discount_rate": float(discount_d["min"]),
                "grid":          grid_opti.tolist(),
            },
            "marker": {
                "cost":      float(cost_d["likely"]),
                "reduction": float(red_d["likely"]),
            },
            "horizon_years": horizon,
            "iterations":    iterations,
            "seed":          seed,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/simulate-sle", methods=["POST"])
def simulate_sle():
    """Run a Single Loss Event simulation (Loss Magnitude only, no LEF)."""
    try:
        data = request.json

        # Build a FAIR model with only LM components
        model = FAIRModel(name=data.get("name", "Single Loss Event"))

        # Handle Loss Magnitude inputs (same logic as /api/simulate)
        if "loss" in data:
            model.lm = parse_distribution(data["loss"])
        elif "primary_loss" in data:
            model.primary_loss = parse_distribution(data["primary_loss"])
            if "secondary_loss_frequency" in data and "secondary_loss_magnitude" in data:
                model.secondary_loss_frequency = parse_distribution(data["secondary_loss_frequency"])
                model.secondary_loss_magnitude = parse_distribution(data["secondary_loss_magnitude"])
        else:
            raise ValueError("Must specify either Loss Magnitude or Primary Loss")

        # Run simulation - sample LM only
        iterations = int(data.get("iterations", 10000))
        seed = int(data.get("seed", 42))
        rng = np.random.default_rng(seed)

        lm_samples = model.sample_lm(iterations, rng)

        # Compute statistics
        summary = {
            "mean": float(np.mean(lm_samples)),
            "median": float(np.median(lm_samples)),
            "std": float(np.std(lm_samples)),
            "min": float(np.min(lm_samples)),
            "max": float(np.max(lm_samples)),
            "p10": float(np.percentile(lm_samples, 10)),
            "p25": float(np.percentile(lm_samples, 25)),
            "p75": float(np.percentile(lm_samples, 75)),
            "p90": float(np.percentile(lm_samples, 90)),
            "p95": float(np.percentile(lm_samples, 95)),
            "var_95": float(np.percentile(lm_samples, 95)),
            "cvar_95": float(np.mean(lm_samples[lm_samples >= np.percentile(lm_samples, 95)])),
        }

        # Generate histogram data
        hist_counts, hist_bins = np.histogram(lm_samples, bins=50)

        # Generate exceedance curve data
        sorted_lm = np.sort(lm_samples)
        exceedance_probs = 1 - np.arange(1, len(sorted_lm) + 1) / len(sorted_lm)
        sample_indices = np.linspace(0, len(sorted_lm) - 1, 100, dtype=int)

        response = {
            "success": True,
            "analysis_type": "sle",
            "summary": summary,
            "histogram": {
                "counts": hist_counts.tolist(),
                "bins": hist_bins.tolist(),
            },
            "exceedance": {
                "values": sorted_lm[sample_indices].tolist(),
                "probabilities": (exceedance_probs[sample_indices] * 100).tolist(),
            },
            "iterations": iterations,
            "seed": seed,
        }

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

    debug = os.environ.get("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")
    app.run(debug=debug, host="0.0.0.0", port=args.port)
