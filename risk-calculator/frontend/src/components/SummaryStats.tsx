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
    <div className="rounded-lg border border-line-grey bg-canvas">
      <div className="px-3 py-2 border-b border-line-grey text-xs text-ink flex items-center justify-between">
        <span>Annualized Loss Expectancy</span>
        <span>iterations: {iterations.toLocaleString()}</span>
      </div>
      <table className="w-full text-sm">
        <tbody>
          {rows.map(([label, value, k]) => (
            <tr key={label} className="border-b border-line-grey last:border-0">
              <td className="px-3 py-1.5 text-ink">{label}</td>
              <td
                className={
                  "px-3 py-1.5 text-right font-mono font-bold text-ink"
                }
              >
                {fmtUsd(value)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
