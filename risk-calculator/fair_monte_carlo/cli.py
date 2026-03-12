"""
Command-line interface for the FAIR Monte Carlo calculator.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np

from fair_monte_carlo.models.fair_model import FAIRModel
from fair_monte_carlo.models.risk_scenario import RiskScenario
from fair_monte_carlo.simulation.monte_carlo import MonteCarloSimulation, simulate
from fair_monte_carlo.distributions.pert import PERTDistribution
from fair_monte_carlo.distributions.lognormal import LogNormalDistribution
from fair_monte_carlo.distributions.uniform import UniformDistribution
from fair_monte_carlo.distributions.constant import ConstantDistribution
from fair_monte_carlo.reporting.report import RiskReport


def parse_distribution(dist_str: str):
    """
    Parse a distribution string into a distribution object.

    Supported formats:
        - constant:value
        - pert:min,likely,max
        - lognormal:low,high
        - uniform:min,max

    Example:
        - "constant:100000"
        - "pert:10000,50000,100000"
        - "lognormal:10000,500000"
    """
    parts = dist_str.split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid distribution format: {dist_str}")

    dist_type = parts[0].lower()
    params = [float(p.strip()) for p in parts[1].split(",")]

    if dist_type == "constant":
        if len(params) != 1:
            raise ValueError("constant requires 1 parameter: value")
        return ConstantDistribution(params[0])

    elif dist_type == "pert":
        if len(params) != 3:
            raise ValueError("pert requires 3 parameters: min,likely,max")
        return PERTDistribution(params[0], params[1], params[2])

    elif dist_type == "lognormal":
        if len(params) != 2:
            raise ValueError("lognormal requires 2 parameters: low,high")
        return LogNormalDistribution(low=params[0], high=params[1])

    elif dist_type == "uniform":
        if len(params) != 2:
            raise ValueError("uniform requires 2 parameters: min,max")
        return UniformDistribution(params[0], params[1])

    else:
        raise ValueError(f"Unknown distribution type: {dist_type}")


def load_scenario_from_json(file_path: str) -> FAIRModel:
    """Load a scenario from a JSON configuration file."""
    with open(file_path) as f:
        config = json.load(f)

    scenario = RiskScenario(
        name=config.get("name", "Unnamed Scenario"),
        description=config.get("description", "")
    )

    # Map config keys to scenario methods
    distribution_mappings = {
        "lef": "with_lef",
        "tef": "with_tef",
        "contact_frequency": "with_contact_frequency",
        "probability_of_action": "with_probability_of_action",
        "vulnerability": "with_vulnerability",
        "threat_capability": "with_threat_capability",
        "resistance_strength": "with_resistance_strength",
        "lm": "with_lm",
        "primary_loss": "with_primary_loss",
        "secondary_loss_frequency": "with_secondary_loss_frequency",
        "secondary_loss_magnitude": "with_secondary_loss_magnitude",
    }

    for key, method_name in distribution_mappings.items():
        if key in config:
            dist_config = config[key]
            if isinstance(dist_config, (int, float)):
                dist = ConstantDistribution(dist_config)
            elif isinstance(dist_config, dict):
                dist_type = dist_config.get("type", "constant").lower()
                if dist_type == "constant":
                    dist = ConstantDistribution(dist_config["value"])
                elif dist_type == "pert":
                    dist = PERTDistribution(
                        dist_config["minimum"],
                        dist_config["most_likely"],
                        dist_config["maximum"],
                        dist_config.get("lambda", 4.0)
                    )
                elif dist_type == "lognormal":
                    if "mu" in dist_config:
                        dist = LogNormalDistribution(
                            mu=dist_config["mu"],
                            sigma=dist_config["sigma"]
                        )
                    else:
                        dist = LogNormalDistribution(
                            low=dist_config["low"],
                            high=dist_config["high"]
                        )
                elif dist_type == "uniform":
                    dist = UniformDistribution(
                        dist_config["minimum"],
                        dist_config["maximum"]
                    )
                else:
                    raise ValueError(f"Unknown distribution type: {dist_type}")
            else:
                raise ValueError(f"Invalid distribution config for {key}")

            method = getattr(scenario, method_name)
            method(dist)

    return scenario.build()


def run_quick_analysis(args) -> int:
    """Run a quick analysis with command-line parameters."""
    print(f"\nRunning FAIR Monte Carlo Analysis: {args.name}")
    print("-" * 50)

    # Build scenario from CLI args
    scenario = RiskScenario(args.name)

    if args.tef:
        scenario.with_tef(parse_distribution(args.tef))

    if args.vulnerability:
        scenario.with_vulnerability(parse_distribution(args.vulnerability))

    if args.loss:
        scenario.with_primary_loss(parse_distribution(args.loss))

    if args.lef:
        scenario.with_lef(parse_distribution(args.lef))

    if args.lm:
        scenario.with_lm(parse_distribution(args.lm))

    model = scenario.build()

    # Run simulation
    sim = MonteCarloSimulation(iterations=args.iterations, seed=args.seed)

    try:
        results = sim.run(model)
    except ValueError as e:
        print(f"Error: {e}")
        print("\nYou must specify either:")
        print("  - LEF directly (--lef) OR TEF (--tef) + Vulnerability (--vulnerability)")
        print("  - LM directly (--lm) OR Primary Loss (--loss)")
        return 1

    # Generate report
    report = RiskReport(results)
    report.print_summary()

    # Save outputs if requested
    if args.output_json:
        with open(args.output_json, 'w') as f:
            f.write(report.to_json())
        print(f"\nJSON output saved to: {args.output_json}")

    if args.output_csv:
        report.to_csv(args.output_csv)
        print(f"CSV output saved to: {args.output_csv}")

    if args.plot:
        report.plot_distribution(save_path=args.plot)
        print(f"Plot saved to: {args.plot}")

    return 0


def run_from_file(args) -> int:
    """Run analysis from a JSON configuration file."""
    print(f"\nLoading scenario from: {args.file}")

    try:
        model = load_scenario_from_json(args.file)
    except Exception as e:
        print(f"Error loading scenario: {e}")
        return 1

    print(f"Running FAIR Monte Carlo Analysis: {model.name}")
    print("-" * 50)

    # Run simulation
    sim = MonteCarloSimulation(iterations=args.iterations, seed=args.seed)
    results = sim.run(model)

    # Generate report
    report = RiskReport(results)
    report.print_summary()

    # Save outputs
    if args.output_json:
        with open(args.output_json, 'w') as f:
            f.write(report.to_json())
        print(f"\nJSON output saved to: {args.output_json}")

    if args.output_csv:
        report.to_csv(args.output_csv)
        print(f"CSV output saved to: {args.output_csv}")

    if args.plot:
        report.plot_distribution(save_path=args.plot)
        print(f"Plot saved to: {args.plot}")

    return 0


def run_demo(args) -> int:
    """Run a demonstration analysis."""
    print("\n" + "=" * 60)
    print("FAIR Monte Carlo Calculator - Demonstration")
    print("=" * 60)

    print("\nScenario: Data Breach Risk Assessment")
    print("-" * 40)
    print("A company is assessing the risk of a data breach affecting")
    print("their customer database containing 100,000 records.")
    print()
    print("Assumptions:")
    print("  - Threat Event Frequency: 5-20 attempts per year (most likely 10)")
    print("  - Vulnerability (probability of success): 10-30% (most likely 20%)")
    print("  - Primary Loss per event: $50K - $500K (log-normal)")
    print("  - Secondary Loss (regulatory fines): 25% chance, $100K - $1M")

    # Build the scenario
    scenario = (RiskScenario("Data Breach")
        .with_tef(PERTDistribution(5, 10, 20))
        .with_vulnerability(PERTDistribution(0.10, 0.20, 0.30))
        .with_primary_loss(LogNormalDistribution(low=50_000, high=500_000))
        .with_secondary_loss(
            frequency=0.25,
            magnitude=LogNormalDistribution(low=100_000, high=1_000_000)
        )
        .build())

    # Run simulation
    print(f"\nRunning {args.iterations:,} Monte Carlo iterations...")
    results = simulate(scenario, iterations=args.iterations, seed=args.seed)

    # Print report
    report = RiskReport(results)
    print()
    report.print_summary()

    print("\nInterpretation:")
    print("-" * 40)
    summary = results.summary()
    print(f"Based on the analysis, there is a 50% chance that annualized losses")
    print(f"will exceed ${summary['ale']['median']:,.0f}.")
    print()
    print(f"In a worst-case scenario (95th percentile), losses could reach")
    print(f"${summary['ale']['percentile_95']:,.0f} per year.")
    print()
    print(f"The average expected loss is ${summary['ale']['mean']:,.0f} per year.")

    if args.plot:
        report.plot_distribution(save_path=args.plot)
        print(f"\nPlot saved to: {args.plot}")

    return 0


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Open FAIR Monte Carlo Risk Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick analysis from command line
  fair-calc quick -n "Phishing Attack" --tef "pert:10,50,100" --vulnerability "pert:0.1,0.2,0.4" --loss "lognormal:5000,50000"

  # Load from configuration file
  fair-calc file scenario.json --iterations 50000

  # Run demonstration
  fair-calc demo

Distribution formats:
  constant:value           - Fixed value
  pert:min,likely,max      - PERT distribution
  lognormal:low,high       - Log-normal (10th/90th percentiles)
  uniform:min,max          - Uniform distribution
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Quick analysis command
    quick_parser = subparsers.add_parser("quick", help="Quick analysis from CLI parameters")
    quick_parser.add_argument("-n", "--name", default="Risk Scenario", help="Scenario name")
    quick_parser.add_argument("--tef", help="Threat Event Frequency distribution")
    quick_parser.add_argument("--vulnerability", help="Vulnerability distribution")
    quick_parser.add_argument("--loss", help="Primary loss distribution")
    quick_parser.add_argument("--lef", help="Loss Event Frequency (alternative to TEF+VULN)")
    quick_parser.add_argument("--lm", help="Loss Magnitude (alternative to --loss)")
    quick_parser.add_argument("-i", "--iterations", type=int, default=10000, help="Number of iterations")
    quick_parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    quick_parser.add_argument("--output-json", help="Save results to JSON file")
    quick_parser.add_argument("--output-csv", help="Save raw data to CSV file")
    quick_parser.add_argument("--plot", help="Save distribution plot to file")

    # File-based analysis command
    file_parser = subparsers.add_parser("file", help="Load scenario from JSON file")
    file_parser.add_argument("file", help="Path to JSON scenario file")
    file_parser.add_argument("-i", "--iterations", type=int, default=10000, help="Number of iterations")
    file_parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    file_parser.add_argument("--output-json", help="Save results to JSON file")
    file_parser.add_argument("--output-csv", help="Save raw data to CSV file")
    file_parser.add_argument("--plot", help="Save distribution plot to file")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run a demonstration analysis")
    demo_parser.add_argument("-i", "--iterations", type=int, default=10000, help="Number of iterations")
    demo_parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    demo_parser.add_argument("--plot", help="Save distribution plot to file")

    args = parser.parse_args()

    if args.command == "quick":
        return run_quick_analysis(args)
    elif args.command == "file":
        return run_from_file(args)
    elif args.command == "demo":
        return run_demo(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
