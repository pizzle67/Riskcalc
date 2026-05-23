import { InputKey, ScenarioMetaKey, useStore } from "../lib/state";
import { simulate } from "../lib/api";

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
  const iterations = useStore((s) => s.iterations);
  const running = useStore((s) => s.running);
  const setResult = useStore((s) => s.setResult);
  const setRunning = useStore((s) => s.setRunning);

  const runScenario = async (alsoPrint: boolean) => {
    setRunning(true);
    try {
      const result = await simulate(inputs, iterations);
      setResult(result);
      if (alsoPrint) {
        setTimeout(() => window.print(), 500);
      }
    } catch (err) {
      console.error("simulate failed", err);
      alert("Simulation failed; check the backend connection.");
    } finally {
      setRunning(false);
    }
  };

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

      <div className="pt-2 flex gap-3 justify-center no-print">
        <button
          onClick={() => runScenario(false)}
          disabled={running}
          className="px-4 py-2 bg-button-grey border border-ink rounded text-ink font-semibold hover:brightness-95 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {running ? "Running..." : "Run Scenario"}
        </button>
        <button
          onClick={() => runScenario(true)}
          disabled={running}
          className="px-4 py-2 bg-button-grey border border-ink rounded text-ink font-semibold hover:brightness-95 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {running ? "Running..." : "Run Scenario and PDF"}
        </button>
      </div>
    </div>
  );
}
