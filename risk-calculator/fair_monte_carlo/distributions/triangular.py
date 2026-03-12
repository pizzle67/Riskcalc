"""Triangular distribution for FAIR analysis."""

from typing import Optional
import numpy as np

from fair_monte_carlo.distributions.base import BaseDistribution


class TriangularDistribution(BaseDistribution):
    """
    Triangular distribution defined by minimum, most likely, and maximum values.

    The triangular distribution is commonly used in Open FAIR for inputs like
    TEF, LEF, Vulnerability, Contact Frequency, and Probability of Action.
    It provides a simple three-point estimate when detailed data is unavailable.

    The distribution forms a triangle shape with:
    - Base from minimum to maximum
    - Peak at the most likely (mode) value
    """

    def __init__(
        self,
        minimum: float,
        most_likely: float,
        maximum: float,
        name: Optional[str] = None
    ):
        """
        Initialize a triangular distribution.

        Args:
            minimum: Minimum possible value (left endpoint)
            most_likely: Most likely value (mode/peak)
            maximum: Maximum possible value (right endpoint)
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

    def sample(self, n: int = 1, random_state: Optional[np.random.Generator] = None) -> np.ndarray:
        """
        Generate random samples from the triangular distribution.

        Args:
            n: Number of samples to generate
            random_state: NumPy random generator for reproducibility

        Returns:
            Array of n random samples
        """
        if random_state is None:
            random_state = np.random.default_rng()

        return random_state.triangular(
            left=self.minimum,
            mode=self.most_likely,
            right=self.maximum,
            size=n
        )

    def mean(self) -> float:
        """
        Return the theoretical mean of the triangular distribution.

        Mean = (min + mode + max) / 3
        """
        return (self.minimum + self.most_likely + self.maximum) / 3

    def describe(self) -> dict:
        """Return distribution parameters."""
        return {
            "minimum": self.minimum,
            "most_likely": self.most_likely,
            "maximum": self.maximum,
        }

    def ppf(self, p: float) -> float:
        """
        Percent point function (inverse CDF) for the triangular distribution.

        Args:
            p: Probability value between 0 and 1

        Returns:
            The value x such that P(X <= x) = p
        """
        a = self.minimum
        b = self.maximum
        c = self.most_likely

        if p < 0 or p > 1:
            raise ValueError(f"p must be between 0 and 1, got {p}")

        # The CDF reaches its peak at F(c) = (c - a) / (b - a)
        fc = (c - a) / (b - a)

        if p <= fc:
            # Left side of the distribution
            return a + np.sqrt(p * (b - a) * (c - a))
        else:
            # Right side of the distribution
            return b - np.sqrt((1 - p) * (b - a) * (b - c))


def triangular(minimum: float, most_likely: float, maximum: float) -> TriangularDistribution:
    """Create a triangular distribution with the given parameters."""
    return TriangularDistribution(minimum, most_likely, maximum)
