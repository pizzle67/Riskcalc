"""
Reporting and visualization for FAIR Monte Carlo results.
"""

from typing import Optional, List, Dict, Any, Union
import numpy as np

from fair_monte_carlo.simulation.monte_carlo import SimulationResults


def _format_currency(value: float, decimals: int = 0) -> str:
    """Format a number as currency."""
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.{decimals}f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:,.{decimals}f}M"
    elif value >= 1_000:
        return f"${value / 1_000:,.{decimals}f}K"
    else:
        return f"${value:,.{decimals}f}"


class RiskReport:
    """
    Generate reports and visualizations from simulation results.
    """

    def __init__(self, results: SimulationResults):
        """
        Initialize report generator.

        Args:
            results: SimulationResults from Monte Carlo simulation
        """
        self.results = results

    def summary_text(self, currency_format: bool = True) -> str:
        """
        Generate a text summary of the risk analysis.

        Args:
            currency_format: Whether to format numbers as currency

        Returns:
            Formatted text summary
        """
        summary = self.results.summary()
        ale = summary["ale"]
        lef = summary["lef"]
        lm = summary["lm"]

        fmt = _format_currency if currency_format else lambda x: f"{x:,.2f}"

        lines = [
            "=" * 60,
            f"FAIR Risk Analysis: {self.results.model_name}",
            "=" * 60,
            "",
            f"Simulation: {self.results.iterations:,} iterations",
            "",
            "ANNUALIZED LOSS EXPECTANCY (ALE)",
            "-" * 40,
            f"  Mean:           {fmt(ale['mean'])}",
            f"  Median:         {fmt(ale['median'])}",
            f"  Std Dev:        {fmt(ale['std'])}",
            f"  Minimum:        {fmt(ale['min'])}",
            f"  Maximum:        {fmt(ale['max'])}",
            "",
            "  Percentiles:",
            f"    10th:         {fmt(ale['percentile_10'])}",
            f"    25th:         {fmt(ale['percentile_25'])}",
            f"    75th:         {fmt(ale['percentile_75'])}",
            f"    90th:         {fmt(ale['percentile_90'])}",
            f"    95th:         {fmt(ale['percentile_95'])}",
            "",
            "  Risk Metrics:",
            f"    VaR (95%):    {fmt(ale['var_95'])}",
            f"    CVaR (95%):   {fmt(ale['cvar_95'])}",
            "",
            "LOSS EVENT FREQUENCY (LEF)",
            "-" * 40,
            f"  Mean:           {lef['mean']:.2f} events/year",
            f"  Median:         {lef['median']:.2f} events/year",
            f"  Range:          {lef['min']:.2f} - {lef['max']:.2f}",
            "",
            "LOSS MAGNITUDE (LM)",
            "-" * 40,
            f"  Mean:           {fmt(lm['mean'])}",
            f"  Median:         {fmt(lm['median'])}",
            f"  Range:          {fmt(lm['min'])} - {fmt(lm['max'])}",
            "",
            "=" * 60,
        ]

        return "\n".join(lines)

    def print_summary(self, currency_format: bool = True):
        """Print the summary to stdout."""
        print(self.summary_text(currency_format))

    def plot_distribution(
        self,
        metric: str = "ale",
        bins: int = 50,
        title: Optional[str] = None,
        figsize: tuple = (10, 6),
        show_stats: bool = True,
        save_path: Optional[str] = None
    ):
        """
        Plot a histogram of the simulation results.

        Args:
            metric: Which metric to plot ("ale", "lef", "lm")
            bins: Number of histogram bins
            title: Custom title (auto-generated if None)
            figsize: Figure size tuple
            show_stats: Whether to show statistics on the plot
            save_path: Path to save the figure (optional)

        Returns:
            matplotlib figure and axes
        """
        import matplotlib.pyplot as plt

        samples = self.results._get_samples(metric)

        fig, ax = plt.subplots(figsize=figsize)

        # Plot histogram
        n, bins_arr, patches = ax.hist(
            samples, bins=bins, density=True,
            alpha=0.7, color='steelblue', edgecolor='white'
        )

        # Add vertical lines for key statistics
        mean_val = np.mean(samples)
        median_val = np.median(samples)
        p95 = np.percentile(samples, 95)

        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {_format_currency(mean_val)}')
        ax.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'Median: {_format_currency(median_val)}')
        ax.axvline(p95, color='orange', linestyle='--', linewidth=2, label=f'95th %ile: {_format_currency(p95)}')

        # Labels and title
        metric_labels = {
            "ale": "Annualized Loss Expectancy",
            "lef": "Loss Event Frequency (events/year)",
            "lm": "Loss Magnitude ($)",
        }
        ax.set_xlabel(metric_labels.get(metric, metric))
        ax.set_ylabel("Density")

        if title:
            ax.set_title(title)
        else:
            ax.set_title(f"{self.results.model_name}: {metric_labels.get(metric, metric)} Distribution")

        if show_stats:
            ax.legend(loc='upper right')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        return fig, ax

    def plot_exceedance_curve(
        self,
        metric: str = "ale",
        title: Optional[str] = None,
        figsize: tuple = (10, 6),
        log_scale: bool = True,
        save_path: Optional[str] = None
    ):
        """
        Plot a loss exceedance curve.

        Shows the probability of exceeding any given loss amount.

        Args:
            metric: Which metric to plot
            title: Custom title
            figsize: Figure size
            log_scale: Use log scale for y-axis
            save_path: Path to save the figure

        Returns:
            matplotlib figure and axes
        """
        import matplotlib.pyplot as plt

        loss_values, exceedance_probs = self.results.exceedance_curve(metric)

        fig, ax = plt.subplots(figsize=figsize)

        ax.plot(loss_values, exceedance_probs * 100, 'b-', linewidth=2)

        # Add reference lines
        ax.axhline(50, color='gray', linestyle=':', alpha=0.5, label='50% probability')
        ax.axhline(10, color='gray', linestyle=':', alpha=0.5, label='10% probability')
        ax.axhline(5, color='gray', linestyle=':', alpha=0.5, label='5% probability')

        ax.set_xlabel("Loss Amount ($)")
        ax.set_ylabel("Probability of Exceedance (%)")

        if title:
            ax.set_title(title)
        else:
            ax.set_title(f"{self.results.model_name}: Loss Exceedance Curve")

        if log_scale:
            ax.set_yscale('log')
            ax.set_ylim(0.1, 100)

        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        return fig, ax

    def plot_comparison(
        self,
        other_results: Union[SimulationResults, List[SimulationResults]],
        metric: str = "ale",
        figsize: tuple = (12, 6),
        title: Optional[str] = None,
        save_path: Optional[str] = None
    ):
        """
        Plot comparison of multiple simulation results.

        Args:
            other_results: One or more SimulationResults to compare
            metric: Which metric to compare
            figsize: Figure size
            title: Custom title
            save_path: Path to save figure

        Returns:
            matplotlib figure and axes
        """
        import matplotlib.pyplot as plt

        if isinstance(other_results, SimulationResults):
            other_results = [other_results]

        all_results = [self.results] + other_results

        fig, axes = plt.subplots(1, 2, figsize=figsize)

        # Histogram comparison
        ax1 = axes[0]
        colors = plt.cm.tab10(np.linspace(0, 1, len(all_results)))

        for i, (result, color) in enumerate(zip(all_results, colors)):
            samples = result._get_samples(metric)
            ax1.hist(samples, bins=30, density=True, alpha=0.5,
                    label=result.model_name, color=color)

        ax1.set_xlabel("Loss Amount ($)")
        ax1.set_ylabel("Density")
        ax1.set_title("Distribution Comparison")
        ax1.legend()

        # Box plot comparison
        ax2 = axes[1]
        data = [r._get_samples(metric) for r in all_results]
        labels = [r.model_name for r in all_results]

        bp = ax2.boxplot(data, labels=labels, patch_artist=True)
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.5)

        ax2.set_ylabel("Loss Amount ($)")
        ax2.set_title("Statistical Comparison")
        ax2.tick_params(axis='x', rotation=45)

        if title:
            fig.suptitle(title, fontsize=14)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        return fig, axes

    def to_dict(self) -> Dict[str, Any]:
        """Export results as a dictionary."""
        return self.results.summary()

    def to_json(self, indent: int = 2) -> str:
        """Export results as JSON string."""
        import json

        def convert(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (np.int64, np.int32)):
                return int(obj)
            if isinstance(obj, (np.float64, np.float32)):
                return float(obj)
            return obj

        summary = self.results.summary()
        return json.dumps(summary, indent=indent, default=convert)

    def to_csv(self, file_path: str):
        """Export raw simulation data to CSV."""
        df = self.results.to_dataframe()
        df.to_csv(file_path, index=False)
        return file_path


def compare_scenarios(
    results_list: List[SimulationResults],
    metric: str = "ale"
) -> Dict[str, Any]:
    """
    Generate a comparison summary across multiple scenarios.

    Args:
        results_list: List of SimulationResults to compare
        metric: Which metric to compare

    Returns:
        Dictionary with comparison statistics
    """
    comparison = {
        "scenarios": [],
        "ranking": [],
    }

    for result in results_list:
        samples = result._get_samples(metric)
        comparison["scenarios"].append({
            "name": result.model_name,
            "mean": float(np.mean(samples)),
            "median": float(np.median(samples)),
            "std": float(np.std(samples)),
            "p95": float(np.percentile(samples, 95)),
        })

    # Rank by mean (lower is better for risk)
    comparison["ranking"] = sorted(
        comparison["scenarios"],
        key=lambda x: x["mean"]
    )

    return comparison
