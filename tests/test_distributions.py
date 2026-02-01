"""Tests for probability distributions."""

import numpy as np
import pytest

from fair_monte_carlo.distributions.pert import PERTDistribution
from fair_monte_carlo.distributions.lognormal import LogNormalDistribution
from fair_monte_carlo.distributions.uniform import UniformDistribution
from fair_monte_carlo.distributions.constant import ConstantDistribution


class TestPERTDistribution:
    """Tests for PERT distribution."""

    def test_basic_creation(self):
        """Test creating a basic PERT distribution."""
        dist = PERTDistribution(10, 20, 30)
        assert dist.minimum == 10
        assert dist.most_likely == 20
        assert dist.maximum == 30

    def test_samples_in_range(self):
        """Test that samples fall within the specified range."""
        dist = PERTDistribution(0, 50, 100)
        rng = np.random.default_rng(42)
        samples = dist.sample(10000, rng)

        assert np.all(samples >= 0)
        assert np.all(samples <= 100)

    def test_mean_approximation(self):
        """Test that sample mean approximates theoretical mean."""
        dist = PERTDistribution(10, 20, 50)
        rng = np.random.default_rng(42)
        samples = dist.sample(100000, rng)

        # Mean should be approximately (min + 4*mode + max) / 6
        expected_mean = (10 + 4 * 20 + 50) / 6
        assert abs(np.mean(samples) - expected_mean) < 1

    def test_invalid_parameters(self):
        """Test that invalid parameters raise errors."""
        with pytest.raises(ValueError):
            PERTDistribution(30, 20, 10)  # min > likely

        with pytest.raises(ValueError):
            PERTDistribution(10, 30, 20)  # likely > max

        with pytest.raises(ValueError):
            PERTDistribution(10, 10, 10)  # all equal


class TestLogNormalDistribution:
    """Tests for log-normal distribution."""

    def test_creation_from_percentiles(self):
        """Test creating from low/high percentile values."""
        dist = LogNormalDistribution(low=1000, high=10000)
        assert dist.mu is not None
        assert dist.sigma > 0

    def test_creation_from_parameters(self):
        """Test creating from mu/sigma parameters."""
        dist = LogNormalDistribution(mu=10, sigma=1)
        assert dist.mu == 10
        assert dist.sigma == 1

    def test_samples_positive(self):
        """Test that samples are always positive."""
        dist = LogNormalDistribution(low=100, high=1000)
        rng = np.random.default_rng(42)
        samples = dist.sample(10000, rng)

        assert np.all(samples > 0)

    def test_percentile_accuracy(self):
        """Test that specified percentiles are accurate."""
        dist = LogNormalDistribution(low=1000, high=10000)
        rng = np.random.default_rng(42)
        samples = dist.sample(100000, rng)

        p10 = np.percentile(samples, 10)
        p90 = np.percentile(samples, 90)

        # Should be close to specified values
        assert abs(p10 - 1000) / 1000 < 0.1  # Within 10%
        assert abs(p90 - 10000) / 10000 < 0.1


class TestUniformDistribution:
    """Tests for uniform distribution."""

    def test_basic_creation(self):
        """Test creating a uniform distribution."""
        dist = UniformDistribution(0, 100)
        assert dist.minimum == 0
        assert dist.maximum == 100

    def test_samples_in_range(self):
        """Test that samples fall within range."""
        dist = UniformDistribution(10, 20)
        rng = np.random.default_rng(42)
        samples = dist.sample(10000, rng)

        assert np.all(samples >= 10)
        assert np.all(samples <= 20)

    def test_mean_accurate(self):
        """Test that sample mean is accurate."""
        dist = UniformDistribution(0, 100)
        rng = np.random.default_rng(42)
        samples = dist.sample(100000, rng)

        assert abs(np.mean(samples) - 50) < 1

    def test_invalid_parameters(self):
        """Test invalid parameters raise error."""
        with pytest.raises(ValueError):
            UniformDistribution(100, 50)  # min >= max


class TestConstantDistribution:
    """Tests for constant distribution."""

    def test_returns_constant(self):
        """Test that all samples are the same value."""
        dist = ConstantDistribution(42)
        samples = dist.sample(100)

        assert np.all(samples == 42)

    def test_mean_is_value(self):
        """Test that mean equals the constant value."""
        dist = ConstantDistribution(123.45)
        assert dist.mean() == 123.45
