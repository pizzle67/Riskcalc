"""Tests for Monte Carlo simulation."""

import numpy as np
import pytest

from fair_monte_carlo.models.risk_scenario import RiskScenario
from fair_monte_carlo.simulation.monte_carlo import (
    MonteCarloSimulation,
    SimulationResults,
    simulate,
)
from fair_monte_carlo.distributions.pert import PERTDistribution
from fair_monte_carlo.distributions.lognormal import LogNormalDistribution
from fair_monte_carlo.distributions.constant import ConstantDistribution


class TestMonteCarloSimulation:
    """Tests for Monte Carlo simulation."""

    @pytest.fixture
    def simple_model(self):
        """Create a simple model for testing."""
        return (RiskScenario("Test")
            .with_tef(PERTDistribution(5, 10, 15))
            .with_vulnerability(0.3)
            .with_primary_loss(LogNormalDistribution(low=10000, high=100000))
            .build())

    def test_basic_simulation(self, simple_model):
        """Test running a basic simulation."""
        sim = MonteCarloSimulation(iterations=1000, seed=42)
        results = sim.run(simple_model)

        assert results.iterations == 1000
        assert len(results.lef_samples) == 1000
        assert len(results.lm_samples) == 1000
        assert len(results.ale_samples) == 1000

    def test_reproducibility(self, simple_model):
        """Test that same seed produces same results."""
        sim1 = MonteCarloSimulation(iterations=1000, seed=42)
        results1 = sim1.run(simple_model)

        sim2 = MonteCarloSimulation(iterations=1000, seed=42)
        results2 = sim2.run(simple_model)

        np.testing.assert_array_equal(results1.ale_samples, results2.ale_samples)

    def test_different_seeds(self, simple_model):
        """Test that different seeds produce different results."""
        sim1 = MonteCarloSimulation(iterations=1000, seed=42)
        results1 = sim1.run(simple_model)

        sim2 = MonteCarloSimulation(iterations=1000, seed=123)
        results2 = sim2.run(simple_model)

        assert not np.array_equal(results1.ale_samples, results2.ale_samples)

    def test_ale_calculation(self):
        """Test that ALE = LEF * LM with Poisson-distributed event counts."""
        model = (RiskScenario("Test")
            .with_lef(ConstantDistribution(10))
            .with_lm(ConstantDistribution(5000))
            .build())

        results = simulate(model, iterations=10000, seed=42)

        # With Poisson discretization, LEF samples are integers around mean=10
        # LEF samples should be non-negative integers
        assert np.all(results.lef_samples >= 0)
        assert np.all(results.lef_samples == results.lef_samples.astype(int))

        # Mean LEF should be approximately 10
        assert abs(np.mean(results.lef_samples) - 10) < 0.2

        # ALE = LEF * LM, so mean ALE should be approximately 10 * 5000 = 50000
        assert abs(np.mean(results.ale_samples) - 50000) < 1000

        # Each sample should be LEF * 5000
        np.testing.assert_array_equal(
            results.ale_samples,
            results.lef_samples * 5000
        )


class TestSimulationResults:
    """Tests for SimulationResults."""

    @pytest.fixture
    def sample_results(self):
        """Create sample results for testing."""
        rng = np.random.default_rng(42)
        n = 10000

        # Create some sample data
        lef = rng.uniform(1, 10, n)
        lm = rng.lognormal(10, 1, n)
        ale = lef * lm

        return SimulationResults(
            model_name="Test Results",
            iterations=n,
            lef_samples=lef,
            lm_samples=lm,
            ale_samples=ale,
            seed=42,
        )

    def test_statistics(self, sample_results):
        """Test statistical methods."""
        mean = sample_results.mean("ale")
        median = sample_results.median("ale")
        std = sample_results.std("ale")

        assert mean > 0
        assert median > 0
        assert std > 0

    def test_percentile(self, sample_results):
        """Test percentile calculation."""
        p10 = sample_results.percentile(10, "ale")
        p50 = sample_results.percentile(50, "ale")
        p90 = sample_results.percentile(90, "ale")

        assert p10 < p50 < p90

    def test_var(self, sample_results):
        """Test Value at Risk calculation."""
        var_95 = sample_results.var(0.95)
        p95 = sample_results.percentile(95)

        assert var_95 == p95

    def test_cvar(self, sample_results):
        """Test Conditional Value at Risk calculation."""
        cvar_95 = sample_results.cvar(0.95)
        var_95 = sample_results.var(0.95)

        # CVaR should be >= VaR
        assert cvar_95 >= var_95

    def test_summary(self, sample_results):
        """Test summary generation."""
        summary = sample_results.summary()

        assert "model_name" in summary
        assert "iterations" in summary
        assert "ale" in summary
        assert "lef" in summary
        assert "lm" in summary

        assert "mean" in summary["ale"]
        assert "var_95" in summary["ale"]

    def test_to_dataframe(self, sample_results):
        """Test conversion to DataFrame."""
        df = sample_results.to_dataframe()

        assert len(df) == sample_results.iterations
        assert "lef" in df.columns
        assert "lm" in df.columns
        assert "ale" in df.columns


class TestScenarioComparison:
    """Tests for scenario comparison functionality."""

    def test_comparison(self):
        """Test comparing two scenarios."""
        baseline = (RiskScenario("Baseline")
            .with_lef(ConstantDistribution(10))
            .with_lm(ConstantDistribution(10000))
            .build())

        improved = (RiskScenario("Improved")
            .with_lef(ConstantDistribution(5))  # Reduced frequency
            .with_lm(ConstantDistribution(10000))
            .build())

        sim = MonteCarloSimulation(iterations=1000, seed=42)
        comparison = sim.run_comparison(baseline, improved)

        assert "baseline" in comparison
        assert "alternative" in comparison
        assert "risk_reduction" in comparison

        # Risk reduction should be positive
        assert comparison["risk_reduction"]["mean"] > 0
