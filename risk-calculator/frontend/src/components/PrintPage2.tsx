import { useStore } from "../lib/state";
import { fmtUsd } from "../lib/compute";
import Histogram from "./Histogram";
import ExceedanceCurve from "./ExceedanceCurve";
import Tornado from "./Tornado";
import { computedMateriality } from "./MaterialityInput";

const FACTOR_LABEL_MAP: Record<string, string> = {
  "Contact Frequency":         "Contact Freq.",
  "Probability of Action":     "Prob. of Action",
  "Threat Capability":         "Threat Capab.",
  "Resistance Strength":       "Resistance Str.",
  "Primary Loss":              "Primary Loss",
  "Secondary Loss Frequency":  "Sec. Loss Freq.",
  "Secondary Loss Magnitude":  "Sec. Loss Mag.",
};

export default function PrintPage2() {
  const result = useStore((s) => s.result);
  const tornado = useStore((s) => s.tornado);
  const materiality = useStore((s) => s.materiality);
  const iterations = useStore((s) => s.iterations);

  const hasResult = result !== null;
  const matValue = computedMateriality(materiality);

  let probExceed = 0;
  if (hasResult) {
    const totalCount = result!.histogram.counts.reduce((a, b) => a + b, 0);
    const exceedCount = result!.histogram.counts.reduce(
      (acc, c, i) => acc + (result!.histogram.bins[i] >= matValue ? c : 0),
      0
    );
    probExceed = totalCount > 0 ? (exceedCount / totalCount) * 100 : 0;
  }

  const summaryRows: [string, number][] = hasResult
    ? [
        ["Mean", result!.summary.mean],
        ["Median", result!.summary.median],
        ["Standard deviation", result!.summary.std],
        ["10th percentile", result!.summary.p10],
        ["90th percentile", result!.summary.p90],
        ["95th percentile (Value at Risk)", result!.summary.var_95],
        ["Conditional VaR (Expected Shortfall)", result!.summary.cvar_95],
      ]
    : [];

  return (
    <div className="print-section">
      <h2 className="text-xl font-bold text-ink mb-3 border-b-2 border-ink pb-1">
        Open FAIR Analysis · Current State
      </h2>

      {hasResult ? (
        <>
          <p className="text-sm text-ink leading-relaxed mb-3">
            The simulation projects an average annualized loss of{" "}
            <strong>{fmtUsd(result!.summary.mean)}</strong>, with a five percent
            chance of exceeding{" "}
            <strong>{fmtUsd(result!.summary.var_95)}</strong>. The expected loss
            in the worst five percent of years averages{" "}
            <strong>{fmtUsd(result!.summary.cvar_95)}</strong>. The probability
            of exceeding the materiality threshold of{" "}
            <strong>{fmtUsd(matValue)}</strong> is{" "}
            <strong>{probExceed.toFixed(1)} percent</strong>. Results are based
            on {iterations.toLocaleString()} Monte Carlo iterations.
          </p>

          <table className="w-full border-collapse border-2 border-ink table-fixed bg-canvas mb-3">
            <thead>
              <tr>
                {summaryRows.map(([label]) => (
                  <th
                    key={label}
                    className="border border-ink px-2 py-1 text-xs font-bold text-ink bg-panel-grey text-center leading-tight"
                  >
                    {label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr>
                {summaryRows.map(([label, value]) => (
                  <td
                    key={label}
                    className="border border-ink px-2 py-1 text-xs font-bold text-ink text-center"
                  >
                    {fmtUsd(value)}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>

          <div className="grid grid-cols-3 gap-3 print-keep-together">
            <div className="rounded-xl border border-ink bg-canvas p-2">
              <h3 className="text-xs font-semibold text-ink mb-1">
                Annualized Loss Expectancy distribution
              </h3>
              <Histogram
                counts={result!.histogram.counts}
                bins={result!.histogram.bins}
                materiality={matValue}
              />
            </div>
            <div className="rounded-xl border border-ink bg-canvas p-2">
              <h3 className="text-xs font-semibold text-ink mb-1">
                Loss exceedance curve
              </h3>
              <ExceedanceCurve
                values={result!.exceedance.values}
                probabilities={result!.exceedance.probabilities}
                materiality={matValue}
                logX
              />
            </div>
            <div className="rounded-xl border border-ink bg-canvas p-2">
              {tornado && tornado.length > 0 ? (
                <Tornado
                  rows={tornado}
                  labelMap={FACTOR_LABEL_MAP}
                  yAxisWidth={88}
                  showMethodology={false}
                  height={240}
                />
              ) : (
                <div className="text-xs text-ink/40 italic">
                  Tornado data unavailable
                </div>
              )}
            </div>
          </div>
        </>
      ) : (
        <div className="print-watermark min-h-[500px]" />
      )}
    </div>
  );
}
