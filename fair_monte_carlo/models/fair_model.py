"""
Core FAIR (Factor Analysis of Information Risk) model implementation.

The FAIR model provides a framework for understanding, analyzing, and
quantifying information risk in financial terms.

Risk Taxonomy:
    Risk = Loss Event Frequency (LEF) × Loss Magnitude (LM)

    LEF = Threat Event Frequency (TEF) × Vulnerability (VULN)
        TEF = Contact Frequency (CF) × Probability of Action (PA)
        VULN = f(Threat Capability, Resistance Strength)

    LM = Primary Loss (PL) + Secondary Loss (SL)
        PL = f(Productivity, Response, Replacement, Fines/Judgments, Competitive Advantage, Reputation)
        SL = Secondary Loss Event Frequency (SLEF) × Secondary Loss Magnitude (SLM)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Union
import numpy as np

from fair_monte_carlo.distributions.base import BaseDistribution
from fair_monte_carlo.distributions.constant import ConstantDistribution


DistributionInput = Union[BaseDistribution, float, int]


def _ensure_distribution(value: DistributionInput) -> BaseDistribution:
    """Convert a value to a distribution if it isn't already."""
    if isinstance(value, BaseDistribution):
        return value
    return ConstantDistribution(float(value))


@dataclass
class FAIRModel:
    """
    Open FAIR risk model for quantitative risk analysis.

    This model implements the complete FAIR taxonomy, allowing you to specify
    distributions for each factor and calculate annualized risk.

    The model supports two approaches:
    1. Direct: Specify LEF and LM directly
    2. Decomposed: Specify component factors (TEF, VULN, etc.) and derive LEF/LM

    Attributes:
        name: Name of the risk scenario
        description: Optional description of the scenario

        # Loss Event Frequency components
        tef: Threat Event Frequency - how often threats act against assets (per year)
        contact_frequency: How often threats contact the asset (per year)
        probability_of_action: Probability a threat acts when it contacts
        vulnerability: Probability an attack succeeds (0-1)
        threat_capability: Threat actor's capability level (0-1)
        resistance_strength: Control effectiveness (0-1)

        # Loss Magnitude components
        primary_loss: Direct losses from the event
        secondary_loss_frequency: Probability of secondary losses (0-1)
        secondary_loss_magnitude: Magnitude of secondary losses
    """

    name: str = "Unnamed Risk Scenario"
    description: str = ""

    # Loss Event Frequency (LEF) - can be specified directly or derived
    _lef: Optional[BaseDistribution] = field(default=None, repr=False)

    # TEF components
    _tef: Optional[BaseDistribution] = field(default=None, repr=False)
    _contact_frequency: Optional[BaseDistribution] = field(default=None, repr=False)
    _probability_of_action: Optional[BaseDistribution] = field(default=None, repr=False)

    # Vulnerability components
    _vulnerability: Optional[BaseDistribution] = field(default=None, repr=False)
    _threat_capability: Optional[BaseDistribution] = field(default=None, repr=False)
    _resistance_strength: Optional[BaseDistribution] = field(default=None, repr=False)

    # Loss Magnitude (LM) - can be specified directly or derived
    _lm: Optional[BaseDistribution] = field(default=None, repr=False)

    # Primary loss
    _primary_loss: Optional[BaseDistribution] = field(default=None, repr=False)

    # Secondary loss components
    _secondary_loss_frequency: Optional[BaseDistribution] = field(default=None, repr=False)
    _secondary_loss_magnitude: Optional[BaseDistribution] = field(default=None, repr=False)

    def __post_init__(self):
        """Validate the model configuration."""
        self._validate()

    def _validate(self):
        """Ensure the model has valid configuration."""
        # Check that we have either LEF or its components
        has_lef = self._lef is not None
        has_tef = self._tef is not None or (
            self._contact_frequency is not None and self._probability_of_action is not None
        )
        has_vuln = self._vulnerability is not None or (
            self._threat_capability is not None and self._resistance_strength is not None
        )

        # Check that we have either LM or its components
        has_lm = self._lm is not None
        has_primary = self._primary_loss is not None
        has_secondary = (
            self._secondary_loss_frequency is not None and
            self._secondary_loss_magnitude is not None
        )

        # At minimum, we need some way to derive both LEF and LM
        # This is validated at simulation time

    # Property setters for LEF components
    @property
    def lef(self) -> Optional[BaseDistribution]:
        """Loss Event Frequency distribution."""
        return self._lef

    @lef.setter
    def lef(self, value: DistributionInput):
        self._lef = _ensure_distribution(value)

    @property
    def tef(self) -> Optional[BaseDistribution]:
        """Threat Event Frequency distribution."""
        return self._tef

    @tef.setter
    def tef(self, value: DistributionInput):
        self._tef = _ensure_distribution(value)

    @property
    def contact_frequency(self) -> Optional[BaseDistribution]:
        """Contact Frequency distribution."""
        return self._contact_frequency

    @contact_frequency.setter
    def contact_frequency(self, value: DistributionInput):
        self._contact_frequency = _ensure_distribution(value)

    @property
    def probability_of_action(self) -> Optional[BaseDistribution]:
        """Probability of Action distribution."""
        return self._probability_of_action

    @probability_of_action.setter
    def probability_of_action(self, value: DistributionInput):
        self._probability_of_action = _ensure_distribution(value)

    @property
    def vulnerability(self) -> Optional[BaseDistribution]:
        """Vulnerability distribution."""
        return self._vulnerability

    @vulnerability.setter
    def vulnerability(self, value: DistributionInput):
        self._vulnerability = _ensure_distribution(value)

    @property
    def threat_capability(self) -> Optional[BaseDistribution]:
        """Threat Capability distribution."""
        return self._threat_capability

    @threat_capability.setter
    def threat_capability(self, value: DistributionInput):
        self._threat_capability = _ensure_distribution(value)

    @property
    def resistance_strength(self) -> Optional[BaseDistribution]:
        """Resistance Strength distribution."""
        return self._resistance_strength

    @resistance_strength.setter
    def resistance_strength(self, value: DistributionInput):
        self._resistance_strength = _ensure_distribution(value)

    # Property setters for LM components
    @property
    def lm(self) -> Optional[BaseDistribution]:
        """Loss Magnitude distribution."""
        return self._lm

    @lm.setter
    def lm(self, value: DistributionInput):
        self._lm = _ensure_distribution(value)

    @property
    def primary_loss(self) -> Optional[BaseDistribution]:
        """Primary Loss distribution."""
        return self._primary_loss

    @primary_loss.setter
    def primary_loss(self, value: DistributionInput):
        self._primary_loss = _ensure_distribution(value)

    @property
    def secondary_loss_frequency(self) -> Optional[BaseDistribution]:
        """Secondary Loss Event Frequency distribution."""
        return self._secondary_loss_frequency

    @secondary_loss_frequency.setter
    def secondary_loss_frequency(self, value: DistributionInput):
        self._secondary_loss_frequency = _ensure_distribution(value)

    @property
    def secondary_loss_magnitude(self) -> Optional[BaseDistribution]:
        """Secondary Loss Magnitude distribution."""
        return self._secondary_loss_magnitude

    @secondary_loss_magnitude.setter
    def secondary_loss_magnitude(self, value: DistributionInput):
        self._secondary_loss_magnitude = _ensure_distribution(value)

    def sample_lef(
        self,
        n: int,
        random_state: Optional[np.random.Generator] = None
    ) -> np.ndarray:
        """
        Sample Loss Event Frequency values.

        If LEF is specified directly, samples from that distribution.
        Otherwise, derives LEF from TEF × Vulnerability.

        Args:
            n: Number of samples
            random_state: Random generator for reproducibility

        Returns:
            Array of LEF samples
        """
        if random_state is None:
            random_state = np.random.default_rng()

        # Direct LEF
        if self._lef is not None:
            return self._lef.sample(n, random_state)

        # Derive TEF
        if self._tef is not None:
            tef_samples = self._tef.sample(n, random_state)
        elif self._contact_frequency is not None and self._probability_of_action is not None:
            cf_samples = self._contact_frequency.sample(n, random_state)
            pa_samples = self._probability_of_action.sample(n, random_state)
            # Clip PA to [0, 1]
            pa_samples = np.clip(pa_samples, 0, 1)
            tef_samples = cf_samples * pa_samples
        else:
            raise ValueError("Must specify either LEF, TEF, or (Contact Frequency + Probability of Action)")

        # Derive Vulnerability
        if self._vulnerability is not None:
            vuln_samples = self._vulnerability.sample(n, random_state)
        elif self._threat_capability is not None and self._resistance_strength is not None:
            tc_samples = self._threat_capability.sample(n, random_state)
            rs_samples = self._resistance_strength.sample(n, random_state)
            # Vulnerability based on comparison of TC vs RS
            # When TC > RS, vulnerability increases
            # Simple model: VULN = max(0, min(1, TC - RS + 0.5))
            vuln_samples = np.clip(tc_samples - rs_samples + 0.5, 0, 1)
        else:
            raise ValueError("Must specify either Vulnerability or (Threat Capability + Resistance Strength)")

        # Clip vulnerability to [0, 1]
        vuln_samples = np.clip(vuln_samples, 0, 1)

        # LEF = TEF × Vulnerability
        return tef_samples * vuln_samples

    def sample_lm(
        self,
        n: int,
        random_state: Optional[np.random.Generator] = None
    ) -> np.ndarray:
        """
        Sample Loss Magnitude values.

        If LM is specified directly, samples from that distribution.
        Otherwise, derives LM from Primary Loss + Secondary Loss.

        Args:
            n: Number of samples
            random_state: Random generator for reproducibility

        Returns:
            Array of LM samples
        """
        if random_state is None:
            random_state = np.random.default_rng()

        # Direct LM
        if self._lm is not None:
            return self._lm.sample(n, random_state)

        # Primary loss is required
        if self._primary_loss is None:
            raise ValueError("Must specify either LM or Primary Loss")

        primary_samples = self._primary_loss.sample(n, random_state)

        # Secondary loss is optional
        if self._secondary_loss_frequency is not None and self._secondary_loss_magnitude is not None:
            slef_samples = self._secondary_loss_frequency.sample(n, random_state)
            slm_samples = self._secondary_loss_magnitude.sample(n, random_state)

            # Clip SLEF to [0, 1]
            slef_samples = np.clip(slef_samples, 0, 1)

            # Secondary loss occurs with probability SLEF
            secondary_occurs = random_state.random(n) < slef_samples
            secondary_loss = np.where(secondary_occurs, slm_samples, 0)

            return primary_samples + secondary_loss
        else:
            return primary_samples

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary representation."""
        result = {
            "name": self.name,
            "description": self.description,
        }

        # Add distribution info for each set parameter
        for attr in [
            "lef", "tef", "contact_frequency", "probability_of_action",
            "vulnerability", "threat_capability", "resistance_strength",
            "lm", "primary_loss", "secondary_loss_frequency", "secondary_loss_magnitude"
        ]:
            dist = getattr(self, f"_{attr}", None)
            if dist is not None:
                result[attr] = dist.describe()

        return result
