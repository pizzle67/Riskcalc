#!/usr/bin/env python3
"""
Basic usage example for the FAIR Monte Carlo Calculator.

This example demonstrates how to create a simple risk scenario,
run a Monte Carlo simulation, and analyze the results.
"""

from fair_monte_carlo import (
    FAIRModel,
    RiskScenario,
    MonteCarloSimulation,
    PERTDistribution,
    LogNormalDistribution,
    RiskReport,
)


def main():
    # Example 1: Simple scenario using the fluent builder
    print("=" * 60)
    print("Example 1: Simple Data Breach Scenario")
    print("=" * 60)

    # Build a risk scenario for a potential data breach
    scenario = (RiskScenario("Data Breach Risk")
        # Threat Event Frequency: 5-20 attacks per year, most likely 10
        .with_tef(PERTDistribution(5, 10, 20))
        # Vulnerability: 10-30% chance of success, most likely 20%
        .with_vulnerability(PERTDistribution(0.10, 0.20, 0.30))
        # Primary loss: $50K-$500K per incident (log-normal)
        .with_primary_loss(LogNormalDistribution(low=50_000, high=500_000))
        .build())

    # Run Monte Carlo simulation
    sim = MonteCarloSimulation(iterations=10_000, seed=42)
    results = sim.run(scenario)

    # Generate and print report
    report = RiskReport(results)
    report.print_summary()

    # Access specific statistics
    print("\nKey Statistics:")
    print(f"  Mean ALE: ${results.mean('ale'):,.0f}")
    print(f"  95% VaR:  ${results.var(0.95):,.0f}")
    print(f"  95% CVaR: ${results.cvar(0.95):,.0f}")


    # Example 2: Advanced scenario with decomposed factors
    print("\n" + "=" * 60)
    print("Example 2: Advanced Ransomware Scenario")
    print("=" * 60)

    ransomware = (RiskScenario("Ransomware Attack")
        # Contact frequency: 100-500 phishing emails per year
        .with_contact_frequency(PERTDistribution(100, 250, 500))
        # Probability of action: 1-5% click through rate
        .with_probability_of_action(PERTDistribution(0.01, 0.02, 0.05))
        # Threat capability vs Resistance strength
        .with_threat_capability(PERTDistribution(0.4, 0.6, 0.8))
        .with_resistance_strength(PERTDistribution(0.3, 0.5, 0.7))
        # Primary loss from ransomware
        .with_primary_loss(LogNormalDistribution(low=100_000, high=1_000_000))
        # Secondary loss (regulatory fines, reputation damage)
        .with_secondary_loss(
            frequency=0.3,  # 30% chance of secondary loss
            magnitude=LogNormalDistribution(low=50_000, high=500_000)
        )
        .build())

    results2 = sim.run(ransomware)
    report2 = RiskReport(results2)
    report2.print_summary()


    # Example 3: Scenario comparison
    print("\n" + "=" * 60)
    print("Example 3: Before/After Control Implementation")
    print("=" * 60)

    # Current state (without MFA)
    current = (RiskScenario("Current State (No MFA)")
        .with_tef(PERTDistribution(10, 20, 50))
        .with_vulnerability(PERTDistribution(0.3, 0.5, 0.7))
        .with_primary_loss(LogNormalDistribution(low=10_000, high=100_000))
        .build())

    # Future state (with MFA implemented)
    with_mfa = (RiskScenario("With MFA")
        .with_tef(PERTDistribution(10, 20, 50))  # Same attack frequency
        .with_vulnerability(PERTDistribution(0.05, 0.10, 0.20))  # Much lower success rate
        .with_primary_loss(LogNormalDistribution(low=10_000, high=100_000))
        .build())

    # Compare scenarios
    comparison = sim.run_comparison(current, with_mfa)

    print(f"\nCurrent State - Mean ALE: ${comparison['baseline'].mean('ale'):,.0f}")
    print(f"With MFA - Mean ALE: ${comparison['alternative'].mean('ale'):,.0f}")
    print(f"\nRisk Reduction:")
    print(f"  Mean: ${comparison['risk_reduction']['mean']:,.0f}")
    print(f"  Median: ${comparison['risk_reduction']['median']:,.0f}")
    print(f"  Probability of positive reduction: {comparison['risk_reduction']['prob_positive_reduction']:.1f}%")


if __name__ == "__main__":
    main()
