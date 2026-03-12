"""Tests for FAIR model."""

import numpy as np
import pytest

from fair_monte_carlo.models.fair_model import FAIRModel
from fair_monte_carlo.models.risk_scenario import RiskScenario, simple_scenario
from fair_monte_carlo.distributions.pert import PERTDistribution
from fair_monte_carlo.distributions.lognormal import LogNormalDistribution
from fair_monte_carlo.distributions.constant import ConstantDistribution


class TestFAIRModel:
    """Tests for the FAIR model."""

    def test_direct_lef_lm(self):
        """Test model with direct LEF and LM."""
        model = FAIRModel(name="Test")
        model.lef = ConstantDistribution(10)
        model.lm = ConstantDistribution(1000)

        rng = np.random.default_rng(42)
        # Use discrete=False to get continuous values for backward compatibility test
        lef = model.sample_lef(100, rng, discrete=False)
        lm = model.sample_lm(100, rng)

        assert np.all(lef == 10)
        assert np.all(lm == 1000)

    def test_discrete_lef_poisson(self):
        """Test that LEF values are converted to discrete counts via Poisson."""
        model = FAIRModel(name="Test")
        model.lef = ConstantDistribution(10)
        model.lm = ConstantDistribution(1000)

        rng = np.random.default_rng(42)
        # Default behavior (discrete=True) uses Poisson
        lef = model.sample_lef(10000, rng, discrete=True)

        # All samples should be non-negative integers
        assert np.all(lef >= 0)
        assert np.all(lef == lef.astype(int))
        # Mean should be approximately the rate (10)
        assert abs(np.mean(lef) - 10) < 0.2

    def test_tef_vulnerability(self):
        """Test model with TEF and Vulnerability."""
        model = FAIRModel(name="Test")
        model.tef = ConstantDistribution(20)
        model.vulnerability = ConstantDistribution(0.5)
        model.primary_loss = ConstantDistribution(5000)

        rng = np.random.default_rng(42)
        # Use discrete=False to test the TEF * Vulnerability calculation
        lef = model.sample_lef(100, rng, discrete=False)

        # LEF = TEF * Vulnerability = 20 * 0.5 = 10
        assert np.allclose(lef, 10)

    def test_decomposed_tef(self):
        """Test model with decomposed TEF (CF * PA)."""
        model = FAIRModel(name="Test")
        model.contact_frequency = ConstantDistribution(100)
        model.probability_of_action = ConstantDistribution(0.1)
        model.vulnerability = ConstantDistribution(0.5)
        model.primary_loss = ConstantDistribution(1000)

        rng = np.random.default_rng(42)
        # Use discrete=False to test the exact calculation
        lef = model.sample_lef(100, rng, discrete=False)

        # TEF = CF * PA = 100 * 0.1 = 10
        # LEF = TEF * VULN = 10 * 0.5 = 5
        assert np.allclose(lef, 5)

    def test_secondary_loss(self):
        """Test model with secondary loss."""
        model = FAIRModel(name="Test")
        model.lef = ConstantDistribution(1)
        model.primary_loss = ConstantDistribution(1000)
        model.secondary_loss_frequency = ConstantDistribution(1.0)  # Always occurs
        model.secondary_loss_magnitude = ConstantDistribution(500)

        rng = np.random.default_rng(42)
        lm = model.sample_lm(100, rng)

        # LM = Primary + Secondary = 1000 + 500 = 1500
        assert np.all(lm == 1500)

    def test_to_dict(self):
        """Test model serialization."""
        model = FAIRModel(name="Test", description="A test scenario")
        model.tef = PERTDistribution(1, 5, 10)
        model.vulnerability = 0.3
        model.primary_loss = LogNormalDistribution(low=1000, high=10000)

        d = model.to_dict()
        assert d["name"] == "Test"
        assert d["description"] == "A test scenario"
        assert "tef" in d
        assert "vulnerability" in d
        assert "primary_loss" in d


class TestRiskScenario:
    """Tests for the RiskScenario builder."""

    def test_fluent_builder(self):
        """Test the fluent builder interface."""
        scenario = (RiskScenario("Test Scenario")
            .with_tef(PERTDistribution(5, 10, 15))
            .with_vulnerability(0.2)
            .with_primary_loss(LogNormalDistribution(low=5000, high=50000))
            .build())

        assert scenario.name == "Test Scenario"
        assert scenario.tef is not None
        assert scenario.vulnerability is not None
        assert scenario.primary_loss is not None

    def test_simple_scenario_helper(self):
        """Test the simple_scenario convenience function."""
        model = simple_scenario(
            name="Quick Test",
            tef_min=1,
            tef_likely=5,
            tef_max=10,
            vulnerability=0.3,
            loss_min=1000,
            loss_likely=5000,
            loss_max=10000
        )

        assert model.name == "Quick Test"
        assert model.tef is not None
        assert model.vulnerability is not None
        assert model.primary_loss is not None

    def test_missing_lef_components(self):
        """Test error when LEF components are missing."""
        model = FAIRModel(name="Incomplete")
        model.primary_loss = ConstantDistribution(1000)

        rng = np.random.default_rng(42)

        with pytest.raises(ValueError, match="Must specify"):
            model.sample_lef(100, rng)

    def test_missing_lm_components(self):
        """Test error when LM components are missing."""
        model = FAIRModel(name="Incomplete")
        model.lef = ConstantDistribution(10)

        rng = np.random.default_rng(42)

        with pytest.raises(ValueError, match="Must specify"):
            model.sample_lm(100, rng)
