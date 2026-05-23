import { fmtUsd } from "../lib/compute";
import { SimResult } from "../lib/state";

type Props = { summary: SimResult["summary"]; iterations: number };

export default function SummaryStats({ summary, iterations }: Props) {
  const rows: [string, number, string?][] = [
    ["Mean ALE", summary.mean],
    ["Median ALE", summary.median],
    ["Standard deviation", summary.std],
    ["10th percentile", summary.p10],
    ["90th percentile", summary.p90],
    ["95th percentile (Value at Risk)", summary.var_95, "var"],
    ["Conditional VaR (Expected Shortfall)", summary.cvar_95, "cvar"],
  ];
  return (
    <div className="space-y-2">
      <div className="text-sm font-bold text-ink px-1">
        The simulation projects an average annual loss of{" "}
        <span className="text-ink">{fmtUsd(summary.mean)}</span>, with a five
        percent chance of exceeding{" "}
        <span className="text-ink">{fmtUsd(summary.var_95)}</span>. The expected
        loss in the worst five percent of years averages{" "}
        <span className="text-ink">{fmtUsd(summary.cvar_95)}</span>. Results are
        based on {iterations.toLocaleString()} Monte Carlo iterations.
      </div>
      <table className="w-full border-collapse border-2 border-ink table-fixed bg-canvas">
        <thead>
          <tr>
            {rows.map(([label]) => (
              <th
                key={label}
                className="border border-ink px-2 py-2 text-sm font-bold text-ink bg-panel-grey text-center leading-tight"
              >
                {label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            {rows.map(([label, value]) => (
              <td
                key={label}
                className="border border-ink px-2 py-2 text-sm font-bold text-ink text-center"
              >
                {fmtUsd(value)}
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}
