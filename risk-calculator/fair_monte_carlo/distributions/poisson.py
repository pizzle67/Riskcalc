"""Poisson distribution for converting continuous rates to discrete event counts."""

from typing import Optional, Union
import numpy as np

from fair_monte_carlo.distributions.base import BaseDistribution


class PoissonDistribution(BaseDistribution):
    """
    Poisson distribution for generating discrete event counts.

    In Open FAIR, this is used to convert continuous Loss Event Frequency (LEF)
    values into discrete integer event counts per simulation trial. Each trial
    year should have an integer number of loss events.

    The distribution can be initialized with either:
    1. A fixed rate (lambda) value
    2. A distribution of rate values - each sample draws from Poisson with
       a rate sampled from this distribution

    The Poisson distribution models the number of events occurring in a fixed
    interval when events occur independently at a constant average rate.
    """

    def __init__(
        self,
        rate: Union[float, BaseDistribution],
        name: Optional[str] = None
    ):
        """
        Initialize a Poisson distribution.

        Args:
            rate: Either a fixed rate (lambda) or a distribution of rates.
                  When a distribution is provided, each sample first draws
                  a rate from that distribution, then samples from Poisson
                  with that rate.
            name: Optional name for the distribution

        Raises:
            ValueError: If rate is negative (for fixed rate)
        """
        super().__init__(name)

        if isinstance(rate, BaseDistribution):
            self.rate_distribution = rate
            self._fixed_rate = None
        else:
            if rate < 0:
                raise ValueError(f"rate must be non-negative, got {rate}")
            self._fixed_rate = float(rate)
            self.rate_distribution = None

    def sample(self, n: int = 1, random_state: Optional[np.random.Generator] = None) -> np.ndarray:
        """
        Generate random samples from the Poisson distribution.

        Args:
            n: Number of samples to generate
            random_state: NumPy random generator for reproducibility

        Returns:
            Array of n non-negative integer samples representing event counts
        """
        if random_state is None:
            random_state = np.random.default_rng()

        if self._fixed_rate is not None:
            # Fixed rate - sample directly from Poisson
            return random_state.poisson(self._fixed_rate, size=n)
        else:
            # Distribution of rates - sample rate first, then Poisson
            rates = self.rate_distribution.sample(n, random_state)
            # Ensure rates are non-negative
            rates = np.maximum(rates, 0)
            # Sample from Poisson with each rate
            return random_state.poisson(rates)

    def mean(self) -> float:
        """
        Return the theoretical mean of the Poisson distribution.

        For Poisson, mean = rate (lambda).
        If using a rate distribution, returns the mean of that distribution.
        """
        if self._fixed_rate is not None:
            return self._fixed_rate
        else:
            return self.rate_distribution.mean()

    def describe(self) -> dict:
        """Return distribution parameters."""
        if self._fixed_rate is not None:
            return {"rate": self._fixed_rate}
        else:
            return {
                "rate_distribution": self.rate_distribution.describe()
            }


def poisson(rate: Union[float, BaseDistribution]) -> PoissonDistribution:
    """Create a Poisson distribution with the given rate or rate distribution."""
    return PoissonDistribution(rate)
