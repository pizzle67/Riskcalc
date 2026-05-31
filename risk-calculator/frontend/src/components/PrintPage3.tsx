import { InputKey, useStore } from "../lib/state";
import { fmtUsd } from "../lib/compute";
import Histogram from "./Histogram";
import ExceedanceCurve from "./ExceedanceCurve";
import Tornado from "./Tornado";

const DECISION_LABEL_MAP: Record<string, string> = {
  "Baseline Annualized Loss Expectancy": "Baseline Loss",
  "Loss Reduction":          "Loss Reduction",
  "Implementation Cost":     "Impl. Cost",
  "Ongoing Operating Cost":  "Ongoing Cost",
  "Discount Rate":           "Discount Rate",
  "Cancellation":            "Cancellation",
};

const FACTOR_ROWS: { key: InputKey; label: string; unit: "usd" | "percent" | "count" }[] = [
  { key: "contactFrequency",       label: "Contact Frequency",        unit: "count"   },
  { key: "probabilityOfAction",    label: "Probability of Action",    unit: "percent" },
  { key: "threatCapability",       label: "Threat Capability",        unit: "percent" },
  { key: "resistanceStrength",     label: "Resistance Strength",      unit: "percent" },
  { key: "primaryLoss",            label: "Primary Loss",             unit: "usd"     },
  { key: "secondaryLossFrequency", label: "Secondary Loss Frequency", unit: "percent" },
  { key: "secondaryLossMagnitude", label: "Secondary Loss Magnitude", unit: "usd"     },
];

function fmtVal(unit: "usd" | "percent" | "count", v: number): string {
  if (unit === "usd") return fmtUsd(v);
  if (unit === "percent") return `${Math.round(v * 100)}%`;
  return `${Math.round(v)}`;
}

export default function PrintPage3() {
  const inputs = useStore((s) => s.inputs);
  const decision = useStore((s) => s.decisionInputs);
  const result = useStore((s) => s.decisionResult);

  const hasResult = result !== null;

  const decisionRows: { label: string; value: string }[] = [
    { label: "Loss Reduction",            value: `${Math.round(decision.lossReduction.likely * 100)}%` },
    { label: "Implementation Cost",       value: fmtUsd(decision.implementationCost.likely) },
    { label: "Ongoing Operating Cost",    value: fmtUsd(decision.ongoingCost.likely) },
    { label: "Discount Rate",             value: `${Math.round(decision.discountRate.likely * 100)}%` },
    { label: "Cancellation Probability",  value: `${Math.round(decision.cancellationProbability * 100)}%` },
    { label: "Time Horizon",              value: `${decision.horizonYears} years` },
    { label: "Ramp-up Year",              value: `${decision.rampUpYear}` },
    { label: "Efficacy Decay per Year",   value: `${Math.round(decision.efficacyDecay * 100)}%` },
    { label: "Salvage Value on Cancel",   value: fmtUsd(decision.salvageValue) },
    { label: "Residual Loss Floor / Year", value: fmtUsd(decision.residualLossFloor) },
  ];

  const cellTh =
    "border border-ink px-3 py-1 text-xs font-semibold text-ink bg-panel-grey text-left";
  const cellTd =
    "border border-ink px-3 py-1 text-xs text-ink";
  const cellVal =
    "border border-ink px-3 py-1 text-xs font-semibold text-ink text-right";

  return (
    <div className="print-section">
      <h2 className="text-xl font-bold text-ink mb-3 border-b-2 border-ink pb-1">
        Decision Analysis
      </h2>

      {/* Two side-by-side input summary tables */}
      <div className="grid grid-cols-2 gap-4 mb-3">
        <div>
          <h3 className="text-xs font-semibold text-ink mb-1">
            Scenario factors (most likely values)
          </h3>
          <table className="w-full border-collapse border-2 border-ink bg-canvas">
            <thead>
              <tr>
                <th className={cellTh}>Factor</th>
                <th className={cellTh + " text-right"}>Input</th>
              </tr>
            </thead>
            <tbody>
              {FACTOR_ROWS.map(({ key, label, unit }) => (
                <tr key={key}>
                  <td className={cellTd}>{label}</td>
                  <td className={cellVal}>
                    {fmtVal(unit, inputs[key].likely)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div>
          <h3 className="text-xs font-semibold text-ink mb-1">
            Decision inputs (most likely values)
          </h3>
          <table className="w-full border-collapse border-2 border-ink bg-canvas">
            <thead>
              <tr>
                <th className={cellTh}>Variable</th>
                <th className={cellTh + " text-right"}>Input</th>
              </tr>
            </thead>
            <tbody>
              {decisionRows.map((r) => (
                <tr key={r.label}>
                  <td className={cellTd}>{r.label}</td>
                  <td className={cellVal}>{r.value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Three NPV charts horizontally */}
      {hasResult ? (
        <div className="grid grid-cols-3 gap-3 print-keep-together">
          <div className="rounded-xl border border-ink bg-canvas p-2">
            <h3 className="text-xs font-semibold text-ink mb-1">
              Net present value distribution
            </h3>
            <Histogram
              counts={result!.histogram.counts}
              bins={result!.histogram.bins}
              materiality={0}
              trialNoun="trials"
              valueLabel="Net present value"
              rangeNoun="a net present value"
            />
          </div>
          <div className="rounded-xl border border-ink bg-canvas p-2">
            <h3 className="text-xs font-semibold text-ink mb-1">
              Risk profile: Net present value
            </h3>
            <ExceedanceCurve
              values={result!.exceedance.values}
              probabilities={result!.exceedance.probabilities}
              materiality={0}
              tooltipLabel={(v) => `Net present value ≥ ${fmtUsd(v)}`}
            />
          </div>
          <div className="rounded-xl border border-ink bg-canvas p-2">
            {result!.tornado && result!.tornado.length > 0 ? (
              <Tornado
                rows={result!.tornado}
                outcomeLabel="net present value"
                labelMap={DECISION_LABEL_MAP}
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
      ) : (
        <div className="print-watermark min-h-[280px]" />
      )}
    </div>
  );
}
