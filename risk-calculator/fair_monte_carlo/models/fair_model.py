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
        random_state: Optional[np.random.Generator] = None,
        discrete: bool = True
    ) -> np.ndarray:
        """
        Sample Loss Event Frequency values.

        If LEF is specified directly, samples from that distribution.
        Otherwise, derives LEF from TEF × Vulnerability.

        Per the Open FAIR guide, LEF values are converted to discrete integer
        event counts using the Poisson distribution. Each simulation trial
        represents a year and should have an integer number of loss events.

        Args:
            n: Number of samples
            random_state: Random generator for reproducibility
            discrete: If True (default), convert continuous LEF to discrete
                     event counts via Poisson distribution

        Returns:
            Array of LEF samples (integers if discrete=True, floats otherwise)
        """
        if random_state is None:
            random_state = np.random.default_rng()

        # Direct LEF
        if self._lef is not None:
            lef_continuous = self._lef.sample(n, random_state)
        else:
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
                # Use the Open FAIR 21x21 grid vulnerability simulator
                # Extract distribution parameters for the vulnerability calculation
                vuln_value = self._calculate_vulnerability_from_distributions()
                # Apply the single vulnerability value to all samples
                vuln_samples = np.full(n, vuln_value)
            else:
                raise ValueError("Must specify either Vulnerability or (Threat Capability + Resistance Strength)")

            # Clip vulnerability to [0, 1]
            vuln_samples = np.clip(vuln_samples, 0, 1)

            # LEF = TEF × Vulnerability
            lef_continuous = tef_samples * vuln_samples

        # Ensure LEF values are non-negative
        lef_continuous = np.maximum(lef_continuous, 0)

        if discrete:
            # Convert continuous LEF to discrete event counts via Poisson
            # For each trial, sample from Poisson(lef_value)
            event_counts = random_state.poisson(lef_continuous)
            return event_counts
        else:
            return lef_continuous

    def _calculate_vulnerability_from_distributions(self) -> float:
        """
        Calculate vulnerability using the Open FAIR 21x21 grid simulator.

        Extracts min/most_likely/max parameters from the Threat Capability
        and Resistance Strength distributions and runs the grid calculation.

        Returns:
            Vulnerability value between 0 and 1
        """
        # Import here to avoid circular import
        from fair_monte_carlo.simulation.vulnerability import calculate_vulnerability_vectorized

        # Extract parameters from threat capability distribution
        tcap_params = self._extract_triangular_params(self._threat_capability)
        rs_params = self._extract_triangular_params(self._resistance_strength)

        return calculate_vulnerability_vectorized(
            tcap_min=tcap_params['minimum'],
            tcap_ml=tcap_params['most_likely'],
            tcap_max=tcap_params['maximum'],
            rs_min=rs_params['minimum'],
            rs_ml=rs_params['most_likely'],
            rs_max=rs_params['maximum']
        )

    def _extract_triangular_params(self, dist: BaseDistribution) -> dict:
        """
        Extract min/most_likely/max parameters from a distribution.

        Supports TriangularDistribution and PERTDistribution directly.
        For ConstantDistribution, uses the constant value for all three.
        For other distributions, attempts to use the describe() method.

        Args:
            dist: A distribution to extract parameters from

        Returns:
            Dictionary with 'minimum', 'most_likely', 'maximum' keys
        """
        # Import here to avoid circular import
        from fair_monte_carlo.distributions.triangular import TriangularDistribution
        from fair_monte_carlo.distributions.pert import PERTDistribution

        if isinstance(dist, (TriangularDistribution, PERTDistribution)):
            return {
                'minimum': dist.minimum,
                'most_likely': dist.most_likely,
                'maximum': dist.maximum
            }
        elif isinstance(dist, ConstantDistribution):
            value = dist.value
            return {
                'minimum': value,
                'most_likely': value,
                'maximum': value
            }
        else:
            # Try to get parameters from describe()
            params = dist.describe()
            if all(k in params for k in ['minimum', 'most_likely', 'maximum']):
                return {
                    'minimum': params['minimum'],
                    'most_likely': params['most_likely'],
                    'maximum': params['maximum']
                }
            # Fallback: use mean for all values (degenerate case)
            mean_val = dist.mean()
            return {
                'minimum': mean_val,
                'most_likely': mean_val,
                'maximum': mean_val
            }

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
