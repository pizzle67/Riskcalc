"""
Risk scenario builder for creating FAIR models with a fluent interface.
"""

from typing import Union, Optional
from fair_monte_carlo.models.fair_model import FAIRModel, DistributionInput
from fair_monte_carlo.distributions.base import BaseDistribution
from fair_monte_carlo.distributions.pert import PERTDistribution
from fair_monte_carlo.distributions.lognormal import LogNormalDistribution
from fair_monte_carlo.distributions.uniform import UniformDistribution
from fair_monte_carlo.distributions.constant import ConstantDistribution


class RiskScenario:
    """
    Fluent builder for creating FAIR risk models.

    Provides a more intuitive interface for constructing risk scenarios
    with method chaining.

    Example:
        scenario = (RiskScenario("Data Breach")
            .with_tef(PERTDistribution(1, 5, 10))
            .with_vulnerability(0.3)
            .with_primary_loss(LogNormalDistribution(low=10000, high=100000))
            .build())
    """

    def __init__(self, name: str, description: str = ""):
        """
        Initialize a new risk scenario.

        Args:
            name: Name of the scenario
            description: Optional description
        """
        self._model = FAIRModel(name=name, description=description)

    @classmethod
    def create(cls, name: str, description: str = "") -> "RiskScenario":
        """Alternative constructor for method chaining."""
        return cls(name, description)

    # LEF components
    def with_lef(self, distribution: DistributionInput) -> "RiskScenario":
        """Set Loss Event Frequency directly."""
        self._model.lef = distribution
        return self

    def with_tef(self, distribution: DistributionInput) -> "RiskScenario":
        """Set Threat Event Frequency."""
        self._model.tef = distribution
        return self

    def with_contact_frequency(self, distribution: DistributionInput) -> "RiskScenario":
        """Set Contact Frequency."""
        self._model.contact_frequency = distribution
        return self

    def with_probability_of_action(self, distribution: DistributionInput) -> "RiskScenario":
        """Set Probability of Action."""
        self._model.probability_of_action = distribution
        return self

    def with_vulnerability(self, distribution: DistributionInput) -> "RiskScenario":
        """Set Vulnerability."""
        self._model.vulnerability = distribution
        return self

    def with_threat_capability(self, distribution: DistributionInput) -> "RiskScenario":
        """Set Threat Capability."""
        self._model.threat_capability = distribution
        return self

    def with_resistance_strength(self, distribution: DistributionInput) -> "RiskScenario":
        """Set Resistance Strength."""
        self._model.resistance_strength = distribution
        return self

    # LM components
    def with_lm(self, distribution: DistributionInput) -> "RiskScenario":
        """Set Loss Magnitude directly."""
        self._model.lm = distribution
        return self

    def with_primary_loss(self, distribution: DistributionInput) -> "RiskScenario":
        """Set Primary Loss."""
        self._model.primary_loss = distribution
        return self

    def with_secondary_loss(
        self,
        frequency: DistributionInput,
        magnitude: DistributionInput
    ) -> "RiskScenario":
        """Set Secondary Loss components."""
        self._model.secondary_loss_frequency = frequency
        self._model.secondary_loss_magnitude = magnitude
        return self

    def with_secondary_loss_frequency(self, distribution: DistributionInput) -> "RiskScenario":
        """Set Secondary Loss Event Frequency."""
        self._model.secondary_loss_frequency = distribution
        return self

    def with_secondary_loss_magnitude(self, distribution: DistributionInput) -> "RiskScenario":
        """Set Secondary Loss Magnitude."""
        self._model.secondary_loss_magnitude = distribution
        return self

    def build(self) -> FAIRModel:
        """Build and return the FAIRModel."""
        return self._model

    @property
    def model(self) -> FAIRModel:
        """Direct access to the underlying model."""
        return self._model


# Convenience functions for quick scenario creation
def simple_scenario(
    name: str,
    tef_min: float,
    tef_likely: float,
    tef_max: float,
    vulnerability: float,
    loss_min: float,
    loss_likely: float,
    loss_max: float,
) -> FAIRModel:
    """
    Create a simple FAIR scenario with PERT distributions.

    Args:
        name: Scenario name
        tef_min: Minimum Threat Event Frequency (events/year)
        tef_likely: Most likely TEF
        tef_max: Maximum TEF
        vulnerability: Probability of successful attack (0-1)
        loss_min: Minimum loss per event
        loss_likely: Most likely loss
        loss_max: Maximum loss

    Returns:
        Configured FAIRModel
    """
    return (RiskScenario(name)
        .with_tef(PERTDistribution(tef_min, tef_likely, tef_max))
        .with_vulnerability(vulnerability)
        .with_primary_loss(PERTDistribution(loss_min, loss_likely, loss_max))
        .build())


def advanced_scenario(
    name: str,
    contact_freq_min: float,
    contact_freq_likely: float,
    contact_freq_max: float,
    prob_action: float,
    threat_capability: float,
    resistance_strength: float,
    primary_loss_low: float,
    primary_loss_high: float,
    secondary_loss_prob: float = 0.0,
    secondary_loss_low: float = 0.0,
    secondary_loss_high: float = 0.0,
) -> FAIRModel:
    """
    Create an advanced FAIR scenario with full decomposition.

    Args:
        name: Scenario name
        contact_freq_min/likely/max: Contact frequency parameters
        prob_action: Probability of action (0-1)
        threat_capability: Threat capability level (0-1)
        resistance_strength: Control strength (0-1)
        primary_loss_low/high: Primary loss range (10th/90th percentiles)
        secondary_loss_prob: Probability of secondary loss (0-1)
        secondary_loss_low/high: Secondary loss range

    Returns:
        Configured FAIRModel
    """
    scenario = (RiskScenario(name)
        .with_contact_frequency(PERTDistribution(contact_freq_min, contact_freq_likely, contact_freq_max))
        .with_probability_of_action(prob_action)
        .with_threat_capability(threat_capability)
        .with_resistance_strength(resistance_strength)
        .with_primary_loss(LogNormalDistribution(low=primary_loss_low, high=primary_loss_high)))

    if secondary_loss_prob > 0 and secondary_loss_high > 0:
        scenario.with_secondary_loss(
            secondary_loss_prob,
            LogNormalDistribution(low=secondary_loss_low, high=secondary_loss_high)
        )

    return scenario.build()
