"""Log-normal distribution for loss magnitude modeling."""

from typing import Optional
import numpy as np
from scipy import stats

from fair_monte_carlo.distributions.base import BaseDistribution


class LogNormalDistribution(BaseDistribution):
    """
    Log-normal distribution.

    Commonly used for modeling loss magnitudes in risk analysis because:
    - Values are always positive
    - Has a long right tail (can model rare but severe losses)
    - Multiplicative processes tend to produce log-normal distributions

    Can be parameterized either by:
    - mu and sigma (parameters of the underlying normal distribution)
    - low and high percentile values (more intuitive for risk estimation)
    """

    def __init__(
        self,
        mu: Optional[float] = None,
        sigma: Optional[float] = None,
        low: Optional[float] = None,
        high: Optional[float] = None,
        low_percentile: float = 0.10,
        high_percentile: float = 0.90,
        name: Optional[str] = None
    ):
        """
        Initialize log-normal distribution.

        Either provide (mu, sigma) OR (low, high) with percentiles.

        Args:
            mu: Mean of the underlying normal distribution (log scale)
            sigma: Standard deviation of the underlying normal (log scale)
            low: Low percentile value
            high: High percentile value
            low_percentile: Percentile for low value (default 0.10 = 10th percentile)
            high_percentile: Percentile for high value (default 0.90 = 90th percentile)
            name: Optional name for the distribution
        """
        super().__init__(name)

        if mu is not None and sigma is not None:
            self.mu = float(mu)
            self.sigma = float(sigma)
            self._from_percentiles = False
        elif low is not None and high is not None:
            if low <= 0 or high <= 0:
                raise ValueError("Low and high values must be positive for log-normal")
            if low >= high:
                raise ValueError("Low value must be less than high value")

            # Convert percentile values to mu and sigma
            z_low = stats.norm.ppf(low_percentile)
            z_high = stats.norm.ppf(high_percentile)

            log_low = np.log(low)
            log_high = np.log(high)

            self.sigma = (log_high - log_low) / (z_high - z_low)
            self.mu = log_low - z_low * self.sigma

            self._from_percentiles = True
            self._low = low
            self._high = high
            self._low_percentile = low_percentile
            self._high_percentile = high_percentile
        else:
            raise ValueError("Must provide either (mu, sigma) or (low, high)")

        if self.sigma <= 0:
            raise ValueError("Sigma must be positive")

    def sample(self, n: int = 1, random_state: Optional[np.random.Generator] = None) -> np.ndarray:
        """Generate random samples from the log-normal distribution."""
        if random_state is None:
            random_state = np.random.default_rng()

        normal_samples = random_state.normal(self.mu, self.sigma, size=n)
        return np.exp(normal_samples)

    def mean(self) -> float:
        """Return the theoretical mean of the log-normal distribution."""
        return np.exp(self.mu + self.sigma**2 / 2)

    def median(self) -> float:
        """Return the median of the log-normal distribution."""
        return np.exp(self.mu)

    def describe(self) -> dict:
        """Return distribution parameters."""
        result = {
            "mu": self.mu,
            "sigma": self.sigma,
            "mean": self.mean(),
            "median": self.median(),
        }
        if self._from_percentiles:
            result.update({
                "low": self._low,
                "high": self._high,
                "low_percentile": self._low_percentile,
                "high_percentile": self._high_percentile,
            })
        return result


# Convenience function
def lognormal(
    low: Optional[float] = None,
    high: Optional[float] = None,
    mu: Optional[float] = None,
    sigma: Optional[float] = None
) -> LogNormalDistribution:
    """Create a log-normal distribution."""
    return LogNormalDistribution(mu=mu, sigma=sigma, low=low, high=high)
