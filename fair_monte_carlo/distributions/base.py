"""Base class for probability distributions."""

from abc import ABC, abstractmethod
from typing import Optional
import numpy as np


class BaseDistribution(ABC):
    """
    Abstract base class for all probability distributions used in FAIR analysis.

    All distributions must implement the sample() method to generate random samples.
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize the distribution.

        Args:
            name: Optional name for the distribution (for reporting)
        """
        self.name = name or self.__class__.__name__

    @abstractmethod
    def sample(self, n: int = 1, random_state: Optional[np.random.Generator] = None) -> np.ndarray:
        """
        Generate random samples from the distribution.

        Args:
            n: Number of samples to generate
            random_state: NumPy random generator for reproducibility

        Returns:
            Array of n random samples
        """
        pass

    @abstractmethod
    def mean(self) -> float:
        """Return the theoretical mean of the distribution."""
        pass

    @abstractmethod
    def describe(self) -> dict:
        """Return a dictionary describing the distribution parameters."""
        pass

    def __repr__(self) -> str:
        params = self.describe()
        param_str = ", ".join(f"{k}={v}" for k, v in params.items())
        return f"{self.__class__.__name__}({param_str})"
