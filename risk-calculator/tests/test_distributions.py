"""Tests for probability distributions."""

import numpy as np
import pytest

from fair_monte_carlo.distributions.pert import PERTDistribution
from fair_monte_carlo.distributions.lognormal import LogNormalDistribution
from fair_monte_carlo.distributions.uniform import UniformDistribution
from fair_monte_carlo.distributions.constant import ConstantDistribution
from fair_monte_carlo.distributions.triangular import TriangularDistribution
from fair_monte_carlo.distributions.poisson import PoissonDistribution
from fair_monte_carlo.simulation.vulnerability import (
    calculate_vulnerability,
    calculate_vulnerability_vectorized
)


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


class TestTriangularDistribution:
    """Tests for triangular distribution."""

    def test_basic_creation(self):
        """Test creating a basic triangular distribution."""
        dist = TriangularDistribution(10, 20, 30)
        assert dist.minimum == 10
        assert dist.most_likely == 20
        assert dist.maximum == 30

    def test_samples_in_range(self):
        """Test that samples fall within the specified range."""
        dist = TriangularDistribution(0, 50, 100)
        rng = np.random.default_rng(42)
        samples = dist.sample(10000, rng)

        assert np.all(samples >= 0)
        assert np.all(samples <= 100)

    def test_mean_approximation(self):
        """Test that sample mean approximates theoretical mean."""
        dist = TriangularDistribution(10, 20, 50)
        rng = np.random.default_rng(42)
        samples = dist.sample(100000, rng)

        # Mean should be approximately (min + mode + max) / 3
        expected_mean = (10 + 20 + 50) / 3
        assert abs(np.mean(samples) - expected_mean) < 0.5

    def test_invalid_parameters(self):
        """Test that invalid parameters raise errors."""
        with pytest.raises(ValueError):
            TriangularDistribution(30, 20, 10)  # min > likely

        with pytest.raises(ValueError):
            TriangularDistribution(10, 30, 20)  # likely > max

        with pytest.raises(ValueError):
            TriangularDistribution(10, 10, 10)  # all equal

    def test_ppf_inverse_cdf(self):
        """Test the percent point function (inverse CDF)."""
        dist = TriangularDistribution(0, 0.5, 1)

        # At p=0, should return minimum
        assert dist.ppf(0) == 0

        # At p=1, should return maximum
        assert dist.ppf(1) == 1

        # ppf should be monotonically increasing
        p_values = [0, 0.25, 0.5, 0.75, 1.0]
        x_values = [dist.ppf(p) for p in p_values]
        assert all(x_values[i] <= x_values[i+1] for i in range(len(x_values)-1))

    def test_skewed_left_distribution(self):
        """Test triangular with mode near minimum (left-skewed)."""
        dist = TriangularDistribution(0, 10, 100)
        rng = np.random.default_rng(42)
        samples = dist.sample(10000, rng)

        # Mode at 10, so median should be less than mean
        assert np.median(samples) < np.mean(samples)

    def test_skewed_right_distribution(self):
        """Test triangular with mode near maximum (right-skewed)."""
        dist = TriangularDistribution(0, 90, 100)
        rng = np.random.default_rng(42)
        samples = dist.sample(10000, rng)

        # Mode at 90, so median should be greater than mean
        assert np.median(samples) > np.mean(samples)


class TestPoissonDistribution:
    """Tests for Poisson distribution."""

    def test_with_constant_rate(self):
        """Test Poisson with a fixed rate."""
        dist = PoissonDistribution(rate=5.0)
        rng = np.random.default_rng(42)
        samples = dist.sample(10000, rng)

        # All samples should be non-negative integers
        assert np.all(samples >= 0)
        assert np.all(samples == samples.astype(int))

        # Mean should be approximately the rate
        assert abs(np.mean(samples) - 5.0) < 0.1

    def test_with_distribution_of_rates(self):
        """Test Poisson with a distribution of rates."""
        # Use uniform rate between 2 and 8, mean = 5
        rate_dist = UniformDistribution(2, 8)
        dist = PoissonDistribution(rate=rate_dist)
        rng = np.random.default_rng(42)
        samples = dist.sample(10000, rng)

        # All samples should be non-negative integers
        assert np.all(samples >= 0)
        assert np.all(samples == samples.astype(int))

        # Mean should be approximately the mean of the rate distribution
        assert abs(np.mean(samples) - 5.0) < 0.2

    def test_outputs_are_integers(self):
        """Test that outputs are always non-negative integers."""
        dist = PoissonDistribution(rate=3.7)
        rng = np.random.default_rng(42)
        samples = dist.sample(1000, rng)

        # Check that all values are integers
        assert samples.dtype in [np.int32, np.int64]
        assert np.all(samples >= 0)

    def test_zero_rate(self):
        """Test Poisson with rate = 0."""
        dist = PoissonDistribution(rate=0)
        samples = dist.sample(100)

        # All samples should be 0
        assert np.all(samples == 0)

    def test_negative_rate_raises_error(self):
        """Test that negative rate raises ValueError."""
        with pytest.raises(ValueError):
            PoissonDistribution(rate=-1)

    def test_mean_with_constant_rate(self):
        """Test that mean() returns the rate."""
        dist = PoissonDistribution(rate=7.5)
        assert dist.mean() == 7.5

    def test_mean_with_rate_distribution(self):
        """Test that mean() returns the mean of the rate distribution."""
        rate_dist = UniformDistribution(4, 6)  # mean = 5
        dist = PoissonDistribution(rate=rate_dist)
        assert dist.mean() == 5.0


class TestVulnerabilitySimulator:
    """Tests for the Open FAIR 21x21 grid vulnerability simulator."""

    def test_known_case_from_guide(self):
        """
        Test known case from Open FAIR guide.

        TCap 15-55-65%, RS 10-50-60% should give approximately 61% vulnerability.
        """
        vuln = calculate_vulnerability(
            tcap_min=0.15, tcap_ml=0.55, tcap_max=0.65,
            rs_min=0.10, rs_ml=0.50, rs_max=0.60
        )
        # Allow some tolerance due to discrete grid approximation
        assert 0.58 < vuln < 0.64, f"Expected ~0.61, got {vuln}"

    def test_rs_much_greater_than_tcap(self):
        """Test that high RS and low TCap gives low vulnerability."""
        vuln = calculate_vulnerability(
            tcap_min=0.05, tcap_ml=0.10, tcap_max=0.15,
            rs_min=0.80, rs_ml=0.90, rs_max=0.95
        )
        # RS >> TCap, so vulnerability should be very low
        assert vuln < 0.05, f"Expected low vulnerability, got {vuln}"

    def test_tcap_much_greater_than_rs(self):
        """Test that high TCap and low RS gives high vulnerability."""
        vuln = calculate_vulnerability(
            tcap_min=0.80, tcap_ml=0.90, tcap_max=0.95,
            rs_min=0.05, rs_ml=0.10, rs_max=0.15
        )
        # TCap >> RS, so vulnerability should be very high
        assert vuln > 0.95, f"Expected high vulnerability, got {vuln}"

    def test_equal_distributions(self):
        """Test that equal TCap and RS gives approximately 50% vulnerability."""
        vuln = calculate_vulnerability(
            tcap_min=0.20, tcap_ml=0.50, tcap_max=0.80,
            rs_min=0.20, rs_ml=0.50, rs_max=0.80
        )
        # Equal distributions should give ~50% vulnerability
        assert 0.45 < vuln < 0.55, f"Expected ~0.50, got {vuln}"

    def test_vectorized_matches_iterative(self):
        """Test that vectorized version matches the iterative version."""
        params = (0.15, 0.55, 0.65, 0.10, 0.50, 0.60)

        vuln_iterative = calculate_vulnerability(*params)
        vuln_vectorized = calculate_vulnerability_vectorized(*params)

        assert abs(vuln_iterative - vuln_vectorized) < 0.001

    def test_vulnerability_bounds(self):
        """Test that vulnerability is always between 0 and 1."""
        test_cases = [
            (0.0, 0.0, 0.01, 0.99, 0.99, 1.0),  # TCap at 0, RS at 1
            (0.99, 0.99, 1.0, 0.0, 0.0, 0.01),  # TCap at 1, RS at 0
            (0.2, 0.5, 0.8, 0.3, 0.6, 0.9),      # Overlapping ranges
        ]

        for params in test_cases:
            vuln = calculate_vulnerability(*params)
            assert 0 <= vuln <= 1, f"Vulnerability {vuln} out of bounds for params {params}"
