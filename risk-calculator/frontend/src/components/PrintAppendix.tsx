import { InputKey, useStore } from "../lib/state";
import { fmtUsd } from "../lib/compute";

const ROWS: { step: number; key: InputKey; label: string; unit: "usd" | "percent" | "count" }[] = [
  { step: 1, key: "contactFrequency",       label: "Contact Frequency",        unit: "count"   },
  { step: 2, key: "probabilityOfAction",    label: "Probability of Action",    unit: "percent" },
  { step: 3, key: "threatCapability",       label: "Threat Capability",        unit: "percent" },
  { step: 4, key: "resistanceStrength",     label: "Resistance Strength",      unit: "percent" },
  { step: 5, key: "primaryLoss",            label: "Primary Loss",             unit: "usd"     },
  { step: 6, key: "secondaryLossFrequency", label: "Secondary Loss Frequency", unit: "percent" },
  { step: 7, key: "secondaryLossMagnitude", label: "Secondary Loss Magnitude", unit: "usd"     },
];

function fmtVal(unit: "usd" | "percent" | "count", v: number): string {
  if (unit === "usd") return fmtUsd(v);
  if (unit === "percent") return `${Math.round(v * 100)}%`;
  return `${Math.round(v)}`;
}

export default function PrintAppendix() {
  const inputs = useStore((s) => s.inputs);
  const baselines = useStore((s) => s.baselines);
  const rationales = useStore((s) => s.rationales);
  const sector = useStore((s) => s.sector);

  const th =
    "border border-ink px-2 py-1 text-xs font-semibold text-ink bg-panel-grey leading-tight";
  const td = "border border-ink px-2 py-1 text-xs text-ink align-top";
  const tdNum = td + " text-right font-mono";

  return (
    <div className="print-section">
      <h2 className="text-xl font-bold text-ink mb-1 border-b-2 border-ink pb-1">
        Appendix · Factor Inputs with Rationale
      </h2>
      <div className="text-xs text-ink/70 mb-3">
        Industry baseline: <strong className="text-ink">{sector}</strong>. The
        baseline column reflects the most-likely value seeded from the selected
        industry; the input columns show the analyst's chosen three-point
        distribution.
      </div>

      <table className="w-full border-collapse border-2 border-ink bg-canvas">
        <thead>
          <tr>
            <th className={th + " w-[44px]"}>Step</th>
            <th className={th}>Factor</th>
            <th className={th + " w-[100px] text-right"}>Baseline</th>
            <th className={th + " w-[80px] text-right"}>Min</th>
            <th className={th + " w-[80px] text-right"}>Likely</th>
            <th className={th + " w-[80px] text-right"}>Max</th>
            <th className={th}>Rationale</th>
          </tr>
        </thead>
        <tbody>
          {ROWS.map(({ step, key, label, unit }) => {
            const baseline = baselines[key].likely;
            const tri = inputs[key];
            const rationale = rationales[key];
            return (
              <tr key={key}>
                <td className={td + " text-center font-mono"}>{step}</td>
                <td className={td}>{label}</td>
                <td className={tdNum}>{fmtVal(unit, baseline)}</td>
                <td className={tdNum}>{fmtVal(unit, tri.min)}</td>
                <td className={tdNum}>{fmtVal(unit, tri.likely)}</td>
                <td className={tdNum}>{fmtVal(unit, tri.max)}</td>
                <td className={td + " whitespace-pre-wrap"}>
                  {rationale || (
                    <span className="text-ink/40 italic">— no rationale provided —</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
