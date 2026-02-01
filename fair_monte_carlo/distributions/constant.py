"""Constant (fixed) value distribution."""

from typing import Optional
import numpy as np

from fair_monte_carlo.distributions.base import BaseDistribution


class ConstantDistribution(BaseDistribution):
    """
    Constant distribution that always returns the same value.

    Useful when a parameter is known with certainty or when you want
    to test scenarios with fixed values.
    """

    def __init__(self, value: float, name: Optional[str] = None):
        """
        Initialize constant distribution.

        Args:
            value: The fixed value to return
            name: Optional name for the distribution
        """
        super().__init__(name)
        self.value = float(value)

    def sample(self, n: int = 1, random_state: Optional[np.random.Generator] = None) -> np.ndarray:
        """Return an array of the constant value."""
        return np.full(n, self.value)

    def mean(self) -> float:
        """Return the constant value."""
        return self.value

    def describe(self) -> dict:
        """Return distribution parameters."""
        return {"value": self.value}


# Convenience function
def constant(value: float) -> ConstantDistribution:
    """Create a constant distribution."""
    return ConstantDistribution(value)
