"""
Open FAIR Monte Carlo Risk Calculator

A Python implementation of the Open FAIR (Factor Analysis of Information Risk)
framework using Monte Carlo simulation for quantitative risk analysis.
"""

from fair_monte_carlo.models.fair_model import FAIRModel
from fair_monte_carlo.models.risk_scenario import RiskScenario
from fair_monte_carlo.simulation.monte_carlo import MonteCarloSimulation
from fair_monte_carlo.distributions.pert import PERTDistribution
from fair_monte_carlo.distributions.lognormal import LogNormalDistribution
from fair_monte_carlo.distributions.uniform import UniformDistribution
from fair_monte_carlo.distributions.constant import ConstantDistribution
from fair_monte_carlo.reporting.report import RiskReport

__version__ = "1.0.0"
__all__ = [
    "FAIRModel",
    "RiskScenario",
    "MonteCarloSimulation",
    "PERTDistribution",
    "LogNormalDistribution",
    "UniformDistribution",
    "ConstantDistribution",
    "RiskReport",
]
