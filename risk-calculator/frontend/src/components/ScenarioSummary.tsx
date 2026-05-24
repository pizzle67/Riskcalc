import { InputKey, ScenarioMetaKey, useStore } from "../lib/state";
import { computedMateriality, METRIC_OPTIONS } from "./MaterialityInput";

const SCOPE_ROWS: { key: ScenarioMetaKey; label: string }[] = [
  { key: "scenarioNumber",  label: "Scenario Number" },
  { key: "asset",           label: "Asset" },
  { key: "threatCommunity", label: "Threat Community" },
  { key: "threatType",      label: "Threat Type" },
  { key: "effect",          label: "Effect" },
];

const FACTOR_ROWS: { key: InputKey; label: string }[] = [
  { key: "contactFrequency",       label: "Contact Frequency" },
  { key: "probabilityOfAction",    label: "Probability of Action" },
  { key: "threatCapability",       label: "Threat Capability" },
  { key: "resistanceStrength",     label: "Resistance Strength" },
  { key: "primaryLoss",            label: "Primary Loss" },
  { key: "secondaryLossFrequency", label: "Secondary Loss Frequency" },
  { key: "secondaryLossMagnitude", label: "Secondary Loss Magnitude" },
];

const isDollar = (k: InputKey) =>
  k === "primaryLoss" || k === "secondaryLossMagnitude";

const isPercent = (k: InputKey) =>
  k === "probabilityOfAction" ||
  k === "threatCapability" ||
  k === "resistanceStrength" ||
  k === "secondaryLossFrequency";

function fmt(key: InputKey, v: number): string {
  const r = Math.round(isPercent(key) ? v * 100 : v);
  if (isDollar(key)) return `$${r.toLocaleString("en-US")}`;
  if (isPercent(key)) return `${r}%`;
  return `${r}`;
}

export default function ScenarioSummary() {
  const meta = useStore((s) => s.scenarioMeta);
  const inputs = useStore((s) => s.inputs);
  const materiality = useStore((s) => s.materiality);

  const matComputed = computedMateriality(materiality);
  const basisLabel =
    METRIC_OPTIONS.find((o) => o.value === materiality.metric)?.label ?? materiality.metric;

  return (
    <div className="space-y-2">
      <table className="w-full border-collapse border-2 border-ink table-fixed bg-canvas">
        <thead>
          <tr>
            {SCOPE_ROWS.map(({ key, label }) => (
              <th
                key={key}
                className="border border-ink px-2 py-2 text-sm font-bold text-ink bg-panel-grey text-center leading-tight"
              >
                {label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            {SCOPE_ROWS.map(({ key }) => (
              <td
                key={key}
                className="border border-ink px-2 py-2 text-sm font-bold text-ink text-center truncate"
              >
                {meta[key] || <span className="text-ink/40 font-bold">—</span>}
              </td>
            ))}
          </tr>
        </tbody>
      </table>

      <table className="w-full border-collapse border-2 border-ink table-fixed bg-canvas">
        <thead>
          <tr>
            {FACTOR_ROWS.map(({ key, label }) => (
              <th
                key={key}
                className="border border-ink px-2 py-2 text-sm font-bold text-ink bg-panel-grey text-center leading-tight"
              >
                {label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            {FACTOR_ROWS.map(({ key }) => (
              <td
                key={key}
                className="border border-ink px-2 py-2 text-sm font-bold text-ink text-center"
              >
                {fmt(key, inputs[key].likely)}
              </td>
            ))}
          </tr>
        </tbody>
      </table>

      <table className="w-full border-collapse border-2 border-ink table-fixed bg-canvas">
        <thead>
          <tr>
            <th className="border border-ink px-2 py-2 text-sm font-bold text-ink bg-panel-grey text-center leading-tight">
              Materiality Basis
            </th>
            <th className="border border-ink px-2 py-2 text-sm font-bold text-ink bg-panel-grey text-center leading-tight">
              Reference Value
            </th>
            <th className="border border-ink px-2 py-2 text-sm font-bold text-ink bg-panel-grey text-center leading-tight">
              Percent Threshold
            </th>
            <th className="border border-ink px-2 py-2 text-sm font-bold text-ink bg-panel-grey text-center leading-tight">
              Computed Materiality
            </th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="border border-ink px-2 py-2 text-sm font-bold text-ink text-center">
              {basisLabel}
            </td>
            <td className="border border-ink px-2 py-2 text-sm font-bold text-ink text-center">
              {`$${Math.round(materiality.value).toLocaleString("en-US")}`}
            </td>
            <td className="border border-ink px-2 py-2 text-sm font-bold text-ink text-center">
              {materiality.metric === "manual" ? "—" : `${materiality.threshold}%`}
            </td>
            <td className="border border-ink px-2 py-2 text-sm font-bold text-ink text-center">
              {`$${Math.round(matComputed).toLocaleString("en-US")}`}
            </td>
          </tr>
        </tbody>
      </table>

    </div>
  );
}
