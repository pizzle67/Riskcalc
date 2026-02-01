"""PERT (Program Evaluation and Review Technique) distribution."""

from typing import Optional
import numpy as np
from scipy import stats

from fair_monte_carlo.distributions.base import BaseDistribution


class PERTDistribution(BaseDistribution):
    """
    PERT distribution (modified beta distribution).

    The PERT distribution is commonly used in risk analysis when you have
    minimum, most likely, and maximum estimates. It's less sensitive to
    extreme values than the triangular distribution.

    The distribution uses the formula:
        mean = (min + 4*mode + max) / 6

    A shape parameter (lambda) controls how peaked the distribution is.
    Default lambda=4 gives the standard PERT distribution.
    """

    def __init__(
        self,
        minimum: float,
        most_likely: float,
        maximum: float,
        lambd: float = 4.0,
        name: Optional[str] = None
    ):
        """
        Initialize PERT distribution.

        Args:
            minimum: Minimum possible value
            most_likely: Most likely value (mode)
            maximum: Maximum possible value
            lambd: Shape parameter (default 4.0 for standard PERT)
            name: Optional name for the distribution

        Raises:
            ValueError: If minimum > most_likely or most_likely > maximum
        """
        super().__init__(name)

        if minimum > most_likely:
            raise ValueError(f"minimum ({minimum}) must be <= most_likely ({most_likely})")
        if most_likely > maximum:
            raise ValueError(f"most_likely ({most_likely}) must be <= maximum ({maximum})")
        if minimum == maximum:
            raise ValueError("minimum and maximum cannot be equal (use ConstantDistribution)")

        self.minimum = float(minimum)
        self.most_likely = float(most_likely)
        self.maximum = float(maximum)
        self.lambd = float(lambd)

        # Calculate beta distribution parameters
        self._range = self.maximum - self.minimum
        self._mu = (self.minimum + self.lambd * self.most_likely + self.maximum) / (self.lambd + 2)

        # Handle edge case where mode equals min or max
        if self.most_likely == self.minimum:
            self._alpha = 1.0
            self._beta = self.lambd
        elif self.most_likely == self.maximum:
            self._alpha = self.lambd
            self._beta = 1.0
        else:
            self._alpha = 1 + self.lambd * (self.most_likely - self.minimum) / self._range
            self._beta = 1 + self.lambd * (self.maximum - self.most_likely) / self._range

    def sample(self, n: int = 1, random_state: Optional[np.random.Generator] = None) -> np.ndarray:
        """Generate random samples from the PERT distribution."""
        if random_state is None:
            random_state = np.random.default_rng()

        # Sample from beta distribution and scale to range
        beta_samples = random_state.beta(self._alpha, self._beta, size=n)
        return self.minimum + beta_samples * self._range

    def mean(self) -> float:
        """Return the theoretical mean of the PERT distribution."""
        return self._mu

    def describe(self) -> dict:
        """Return distribution parameters."""
        return {
            "minimum": self.minimum,
            "most_likely": self.most_likely,
            "maximum": self.maximum,
            "lambda": self.lambd,
        }


# Convenience function
def pert(minimum: float, most_likely: float, maximum: float, lambd: float = 4.0) -> PERTDistribution:
    """Create a PERT distribution with the given parameters."""
    return PERTDistribution(minimum, most_likely, maximum, lambd)
