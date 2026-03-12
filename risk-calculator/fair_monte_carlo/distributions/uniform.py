"""Uniform distribution."""

from typing import Optional
import numpy as np

from fair_monte_carlo.distributions.base import BaseDistribution


class UniformDistribution(BaseDistribution):
    """
    Uniform distribution between minimum and maximum values.

    Useful when you only know the range of possible values and have
    no information about which values are more likely.
    """

    def __init__(
        self,
        minimum: float,
        maximum: float,
        name: Optional[str] = None
    ):
        """
        Initialize uniform distribution.

        Args:
            minimum: Minimum value
            maximum: Maximum value
            name: Optional name for the distribution
        """
        super().__init__(name)

        if minimum >= maximum:
            raise ValueError(f"minimum ({minimum}) must be < maximum ({maximum})")

        self.minimum = float(minimum)
        self.maximum = float(maximum)

    def sample(self, n: int = 1, random_state: Optional[np.random.Generator] = None) -> np.ndarray:
        """Generate random samples from the uniform distribution."""
        if random_state is None:
            random_state = np.random.default_rng()

        return random_state.uniform(self.minimum, self.maximum, size=n)

    def mean(self) -> float:
        """Return the theoretical mean of the uniform distribution."""
        return (self.minimum + self.maximum) / 2

    def describe(self) -> dict:
        """Return distribution parameters."""
        return {
            "minimum": self.minimum,
            "maximum": self.maximum,
        }


# Convenience function
def uniform(minimum: float, maximum: float) -> UniformDistribution:
    """Create a uniform distribution."""
    return UniformDistribution(minimum, maximum)
