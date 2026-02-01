# Open FAIR Monte Carlo Calculator

A Python implementation of the Open FAIR (Factor Analysis of Information Risk) framework using Monte Carlo simulation for quantitative risk analysis.

## Overview

This calculator helps organizations quantify information security risk in financial terms by:

- Modeling risk factors using probability distributions
- Running Monte Carlo simulations to account for uncertainty
- Producing actionable risk metrics like VaR and Expected Loss

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd Riskcalc

# Install with pip
pip install -e .

# Or install dependencies directly
pip install numpy scipy matplotlib pandas
```

## Quick Start

### Python API

```python
from fair_monte_carlo import (
    RiskScenario,
    MonteCarloSimulation,
    PERTDistribution,
    LogNormalDistribution,
    RiskReport,
)

# Build a risk scenario
scenario = (RiskScenario("Data Breach Risk")
    .with_tef(PERTDistribution(5, 10, 20))           # 5-20 attacks/year
    .with_vulnerability(PERTDistribution(0.1, 0.2, 0.3))  # 10-30% success rate
    .with_primary_loss(LogNormalDistribution(low=50_000, high=500_000))
    .build())

# Run simulation
sim = MonteCarloSimulation(iterations=10_000, seed=42)
results = sim.run(scenario)

# Generate report
report = RiskReport(results)
report.print_summary()

# Access specific metrics
print(f"Mean Annual Loss: ${results.mean('ale'):,.0f}")
print(f"95% VaR: ${results.var(0.95):,.0f}")
```

### Command Line

```bash
# Run a demonstration
fair-calc demo

# Quick analysis from CLI
fair-calc quick -n "Phishing Attack" \
    --tef "pert:10,50,100" \
    --vulnerability "pert:0.1,0.2,0.4" \
    --loss "lognormal:5000,50000"

# Load from JSON configuration
fair-calc file scenario.json --iterations 50000 --output-json results.json
```

## FAIR Model Components

The Open FAIR model decomposes risk into:

```
Risk = Loss Event Frequency (LEF) × Loss Magnitude (LM)

LEF = Threat Event Frequency (TEF) × Vulnerability (VULN)
    TEF = Contact Frequency (CF) × Probability of Action (PA)
    VULN = f(Threat Capability, Resistance Strength)

LM = Primary Loss + Secondary Loss
    Secondary Loss = SL Frequency × SL Magnitude
```

### Supported Distributions

| Distribution | Parameters | Use Case |
|-------------|------------|----------|
| PERT | min, likely, max | Expert estimates with bounds |
| Log-normal | low, high (percentiles) | Loss magnitudes, right-skewed data |
| Uniform | min, max | Unknown distribution within range |
| Constant | value | Fixed/known values |

## Examples

### Simple Scenario

```python
from fair_monte_carlo import RiskScenario, PERTDistribution, simulate, RiskReport

model = (RiskScenario("Ransomware")
    .with_tef(PERTDistribution(1, 3, 10))
    .with_vulnerability(0.25)
    .with_primary_loss(PERTDistribution(50_000, 200_000, 1_000_000))
    .build())

results = simulate(model, iterations=10_000)
RiskReport(results).print_summary()
```

### Scenario Comparison

```python
from fair_monte_carlo import RiskScenario, MonteCarloSimulation

# Before implementing a control
baseline = (RiskScenario("Without MFA")
    .with_tef(10)
    .with_vulnerability(0.5)
    .with_primary_loss(100_000)
    .build())

# After implementing MFA
with_mfa = (RiskScenario("With MFA")
    .with_tef(10)
    .with_vulnerability(0.1)  # Reduced vulnerability
    .with_primary_loss(100_000)
    .build())

sim = MonteCarloSimulation(iterations=10_000)
comparison = sim.run_comparison(baseline, with_mfa)

print(f"Risk Reduction: ${comparison['risk_reduction']['mean']:,.0f}")
```

### JSON Configuration

```json
{
    "name": "Insider Threat",
    "tef": {
        "type": "pert",
        "minimum": 2,
        "most_likely": 5,
        "maximum": 15
    },
    "vulnerability": {
        "type": "pert",
        "minimum": 0.2,
        "most_likely": 0.4,
        "maximum": 0.6
    },
    "primary_loss": {
        "type": "lognormal",
        "low": 100000,
        "high": 1000000
    }
}
```

## Output Metrics

The calculator provides:

- **Mean/Median ALE**: Average expected annual loss
- **Percentiles**: 10th, 25th, 75th, 90th, 95th
- **VaR (Value at Risk)**: Loss threshold at confidence level
- **CVaR (Conditional VaR)**: Expected loss in worst-case scenarios
- **Loss Exceedance Curves**: Probability of exceeding loss thresholds

## Running Tests

```bash
pip install pytest pytest-cov
pytest tests/ -v
```

## Project Structure

```
fair_monte_carlo/
├── __init__.py
├── cli.py                    # Command-line interface
├── models/
│   ├── fair_model.py         # Core FAIR model
│   └── risk_scenario.py      # Fluent builder
├── distributions/
│   ├── base.py               # Base distribution class
│   ├── pert.py               # PERT distribution
│   ├── lognormal.py          # Log-normal distribution
│   ├── uniform.py            # Uniform distribution
│   └── constant.py           # Constant value
├── simulation/
│   └── monte_carlo.py        # Monte Carlo engine
└── reporting/
    └── report.py             # Reports and visualization
```

## References

- [The Open Group - Open FAIR](https://www.opengroup.org/forum/open-fair-forum)
- [FAIR Institute](https://www.fairinstitute.org/)
- Freund, J., & Jones, J. (2014). *Measuring and Managing Information Risk: A FAIR Approach*

## License

MIT License
