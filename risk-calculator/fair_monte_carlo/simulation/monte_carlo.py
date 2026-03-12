"""
Monte Carlo simulation engine for FAIR risk analysis.

Runs multiple iterations sampling from the specified distributions
to produce a probability distribution of potential risk outcomes.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Union
import numpy as np
import pandas as pd
from scipy import stats

from fair_monte_carlo.models.fair_model import FAIRModel


@dataclass
class SimulationResults:
    """
    Container for Monte Carlo simulation results.

    Attributes:
        model_name: Name of the risk scenario
        iterations: Number of simulation iterations
        lef_samples: Array of Loss Event Frequency samples
        lm_samples: Array of Loss Magnitude samples
        ale_samples: Array of Annualized Loss Expectancy samples (LEF × LM)
        seed: Random seed used for reproducibility
    """
    model_name: str
    iterations: int
    lef_samples: np.ndarray
    lm_samples: np.ndarray
    ale_samples: np.ndarray
    seed: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def risk(self) -> np.ndarray:
        """Alias for ale_samples."""
        return self.ale_samples

    def percentile(self, p: float, metric: str = "ale") -> float:
        """
        Get the value at a specific percentile.

        Args:
            p: Percentile (0-100)
            metric: Which metric - "ale", "lef", or "lm"

        Returns:
            Value at the specified percentile
        """
        samples = self._get_samples(metric)
        return np.percentile(samples, p)

    def mean(self, metric: str = "ale") -> float:
        """Get the mean value of a metric."""
        return np.mean(self._get_samples(metric))

    def median(self, metric: str = "ale") -> float:
        """Get the median value of a metric."""
        return np.median(self._get_samples(metric))

    def std(self, metric: str = "ale") -> float:
        """Get the standard deviation of a metric."""
        return np.std(self._get_samples(metric))

    def var(self, confidence: float = 0.95, metric: str = "ale") -> float:
        """
        Calculate Value at Risk at the specified confidence level.

        Args:
            confidence: Confidence level (e.g., 0.95 for 95%)
            metric: Which metric to calculate VaR for

        Returns:
            VaR value
        """
        return self.percentile(confidence * 100, metric)

    def cvar(self, confidence: float = 0.95, metric: str = "ale") -> float:
        """
        Calculate Conditional Value at Risk (Expected Shortfall).

        The average loss in the worst (1-confidence) of cases.

        Args:
            confidence: Confidence level (e.g., 0.95 for 95%)
            metric: Which metric to calculate CVaR for

        Returns:
            CVaR value
        """
        samples = self._get_samples(metric)
        var_threshold = self.var(confidence, metric)
        tail_samples = samples[samples >= var_threshold]
        return np.mean(tail_samples) if len(tail_samples) > 0 else var_threshold

    def _get_samples(self, metric: str) -> np.ndarray:
        """Get samples for the specified metric."""
        if metric == "ale" or metric == "risk":
            return self.ale_samples
        elif metric == "lef":
            return self.lef_samples
        elif metric == "lm":
            return self.lm_samples
        else:
            raise ValueError(f"Unknown metric: {metric}. Use 'ale', 'lef', or 'lm'")

    def summary(self) -> Dict[str, Any]:
        """Generate a summary of the simulation results."""
        return {
            "model_name": self.model_name,
            "iterations": self.iterations,
            "ale": {
                "mean": self.mean("ale"),
                "median": self.median("ale"),
                "std": self.std("ale"),
                "min": np.min(self.ale_samples),
                "max": np.max(self.ale_samples),
                "percentile_10": self.percentile(10, "ale"),
                "percentile_25": self.percentile(25, "ale"),
                "percentile_75": self.percentile(75, "ale"),
                "percentile_90": self.percentile(90, "ale"),
                "percentile_95": self.percentile(95, "ale"),
                "var_95": self.var(0.95, "ale"),
                "cvar_95": self.cvar(0.95, "ale"),
            },
            "lef": {
                "mean": self.mean("lef"),
                "median": self.median("lef"),
                "std": self.std("lef"),
                "min": np.min(self.lef_samples),
                "max": np.max(self.lef_samples),
            },
            "lm": {
                "mean": self.mean("lm"),
                "median": self.median("lm"),
                "std": self.std("lm"),
                "min": np.min(self.lm_samples),
                "max": np.max(self.lm_samples),
            },
        }

    def to_dataframe(self) -> pd.DataFrame:
        """Convert results to a pandas DataFrame."""
        return pd.DataFrame({
            "lef": self.lef_samples,
            "lm": self.lm_samples,
            "ale": self.ale_samples,
        })

    def exceedance_curve(self, metric: str = "ale", points: int = 100) -> tuple:
        """
        Generate loss exceedance curve data.

        Returns:
            Tuple of (loss_values, exceedance_probabilities)
        """
        samples = self._get_samples(metric)
        sorted_samples = np.sort(samples)
        exceedance = 1 - np.arange(1, len(sorted_samples) + 1) / len(sorted_samples)

        # Downsample to specified number of points
        if len(sorted_samples) > points:
            indices = np.linspace(0, len(sorted_samples) - 1, points, dtype=int)
            sorted_samples = sorted_samples[indices]
            exceedance = exceedance[indices]

        return sorted_samples, exceedance


class MonteCarloSimulation:
    """
    Monte Carlo simulation engine for FAIR risk models.

    Runs multiple iterations of the risk model, sampling from all
    specified probability distributions to produce a distribution
    of possible risk outcomes.
    """

    def __init__(
        self,
        iterations: int = 10000,
        seed: Optional[int] = None
    ):
        """
        Initialize the simulation engine.

        Args:
            iterations: Number of Monte Carlo iterations (default 10,000)
            seed: Random seed for reproducibility
        """
        self.iterations = iterations
        self.seed = seed
        self._rng: Optional[np.random.Generator] = None

    def run(
        self,
        model: FAIRModel,
        iterations: Optional[int] = None,
        seed: Optional[int] = None
    ) -> SimulationResults:
        """
        Run Monte Carlo simulation on a FAIR model.

        Args:
            model: The FAIRModel to simulate
            iterations: Override default iterations for this run
            seed: Override default seed for this run

        Returns:
            SimulationResults containing the simulation outputs
        """
        n = iterations or self.iterations
        run_seed = seed if seed is not None else self.seed

        # Create random generator
        self._rng = np.random.default_rng(run_seed)

        # Sample LEF and LM
        lef_samples = model.sample_lef(n, self._rng)
        lm_samples = model.sample_lm(n, self._rng)

        # Calculate ALE (Annualized Loss Expectancy)
        ale_samples = lef_samples * lm_samples

        return SimulationResults(
            model_name=model.name,
            iterations=n,
            lef_samples=lef_samples,
            lm_samples=lm_samples,
            ale_samples=ale_samples,
            seed=run_seed,
            metadata=model.to_dict(),
        )

    def run_multiple(
        self,
        models: List[FAIRModel],
        iterations: Optional[int] = None,
        seed: Optional[int] = None
    ) -> Dict[str, SimulationResults]:
        """
        Run simulations on multiple FAIR models.

        Args:
            models: List of FAIRModels to simulate
            iterations: Override default iterations
            seed: Base seed (each model gets seed + index)

        Returns:
            Dictionary mapping model names to results
        """
        results = {}
        for i, model in enumerate(models):
            model_seed = (seed + i) if seed is not None else None
            results[model.name] = self.run(model, iterations, model_seed)
        return results

    def run_comparison(
        self,
        baseline: FAIRModel,
        alternative: FAIRModel,
        iterations: Optional[int] = None,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Compare two scenarios (e.g., before/after a control implementation).

        Args:
            baseline: The baseline scenario
            alternative: The alternative scenario
            iterations: Number of iterations
            seed: Random seed

        Returns:
            Dictionary with comparison results
        """
        n = iterations or self.iterations
        run_seed = seed if seed is not None else self.seed
        rng = np.random.default_rng(run_seed)

        # Run both simulations with same random state for paired comparison
        baseline_lef = baseline.sample_lef(n, rng)
        baseline_lm = baseline.sample_lm(n, rng)
        baseline_ale = baseline_lef * baseline_lm

        # Reset RNG for alternative (or use different seed)
        rng = np.random.default_rng(run_seed + 1 if run_seed else None)
        alt_lef = alternative.sample_lef(n, rng)
        alt_lm = alternative.sample_lm(n, rng)
        alt_ale = alt_lef * alt_lm

        # Calculate risk reduction
        risk_reduction = baseline_ale - alt_ale
        relative_reduction = np.where(
            baseline_ale > 0,
            risk_reduction / baseline_ale * 100,
            0
        )

        return {
            "baseline": SimulationResults(
                model_name=baseline.name,
                iterations=n,
                lef_samples=baseline_lef,
                lm_samples=baseline_lm,
                ale_samples=baseline_ale,
                seed=run_seed,
            ),
            "alternative": SimulationResults(
                model_name=alternative.name,
                iterations=n,
                lef_samples=alt_lef,
                lm_samples=alt_lm,
                ale_samples=alt_ale,
                seed=run_seed,
            ),
            "risk_reduction": {
                "mean": np.mean(risk_reduction),
                "median": np.median(risk_reduction),
                "std": np.std(risk_reduction),
                "percentile_5": np.percentile(risk_reduction, 5),
                "percentile_95": np.percentile(risk_reduction, 95),
                "prob_positive_reduction": np.mean(risk_reduction > 0) * 100,
            },
            "relative_reduction_pct": {
                "mean": np.mean(relative_reduction),
                "median": np.median(relative_reduction),
            },
        }


# Convenience function
def simulate(
    model: FAIRModel,
    iterations: int = 10000,
    seed: Optional[int] = None
) -> SimulationResults:
    """
    Run a Monte Carlo simulation on a FAIR model.

    Args:
        model: The FAIRModel to simulate
        iterations: Number of iterations (default 10,000)
        seed: Random seed for reproducibility

    Returns:
        SimulationResults
    """
    sim = MonteCarloSimulation(iterations, seed)
    return sim.run(model)
