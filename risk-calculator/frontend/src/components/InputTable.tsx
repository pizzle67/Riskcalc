import * as Slider from "@radix-ui/react-slider";
import { InputKey, INPUT_META, useStore } from "../lib/state";

const ROWS: { step: number; key: InputKey; unit: string }[] = [
  { step: 1, key: "contactFrequency",       unit: "per year"     },
  { step: 2, key: "probabilityOfAction",    unit: "percent"      },
  { step: 3, key: "threatCapability",       unit: "percent"      },
  { step: 4, key: "resistanceStrength",     unit: "percent"      },
  { step: 5, key: "primaryLoss",            unit: "USD"          },
  { step: 6, key: "secondaryLossFrequency", unit: "percent"      },
  { step: 7, key: "secondaryLossMagnitude", unit: "USD"          },
];

const isDollar = (k: InputKey) =>
  k === "primaryLoss" || k === "secondaryLossMagnitude";

const isPercent = (k: InputKey) =>
  k === "probabilityOfAction" ||
  k === "threatCapability" ||
  k === "resistanceStrength" ||
  k === "secondaryLossFrequency";

function fmtForUnit(key: InputKey, v: number): string {
  const rounded = Math.round(isPercent(key) ? v * 100 : v);
  if (isDollar(key)) return `$${rounded.toLocaleString("en-US")}`;
  if (isPercent(key)) return `${rounded}%`;
  return `${rounded}`;
}

function parseForUnit(key: InputKey, str: string): number | null {
  const cleaned = str.replace(/[^0-9.-]/g, "");
  if (cleaned === "" || cleaned === "-") return 0;
  const n = parseFloat(cleaned);
  if (!Number.isFinite(n)) return null;
  return isPercent(key) ? n / 100 : n;
}

const LABELS: Record<InputKey, string> = {
  contactFrequency:       "Contact Frequency",
  probabilityOfAction:    "Probability of Action",
  threatCapability:       "Threat Capability",
  resistanceStrength:     "Resistance Strength",
  primaryLoss:            "Primary Loss",
  secondaryLossFrequency: "Secondary Loss Frequency",
  secondaryLossMagnitude: "Secondary Loss Magnitude",
};

export default function InputTable() {
  const inputs = useStore((s) => s.inputs);
  const baselines = useStore((s) => s.baselines);
  const rationales = useStore((s) => s.rationales);
  const setLikely = useStore((s) => s.setLikelyProportional);
  const setRationale = useStore((s) => s.setRationale);
  const tableFrozen = useStore((s) => s.tableFrozen);

  const thBase =
    "border border-ink px-3 py-2 text-sm font-semibold text-ink bg-panel-grey";
  const thSticky = tableFrozen ? " sticky top-0 z-10" : "";

  return (
    <div
      className={
        "rounded-xl border-2 border-ink bg-canvas " +
        (tableFrozen ? "max-h-[460px] overflow-y-auto" : "overflow-hidden")
      }
    >
      <table className="w-full border-collapse table-fixed">
        <thead>
          <tr>
            <th className={`${thBase}${thSticky} w-[64px]`}>Step</th>
            <th className={`${thBase}${thSticky} w-[200px]`}>Factor</th>
            <th className={`${thBase}${thSticky} w-[150px]`}>Factor Baseline</th>
            <th className={`${thBase}${thSticky} w-[160px]`}>Factor Input</th>
            <th className={`${thBase}${thSticky} w-[140px]`}>Unit</th>
            <th className={`${thBase}${thSticky}`}>Input Rationale</th>
          </tr>
        </thead>
        <tbody>
          {ROWS.map(({ step, key, unit }) => {
            const label = LABELS[key];
            const baseline = baselines[key].likely;
            const current = inputs[key].likely;
            return (
              <tr key={key} className="border-b border-ink last:border-0">
                <td className="border border-ink px-3 py-4 text-sm text-ink text-center font-mono align-middle">
                  {step}
                </td>
                <td className="border border-ink px-3 py-4 text-sm text-ink align-middle">
                  {label}
                </td>
                <td className="border border-ink px-3 py-4 text-sm text-ink text-right font-mono align-middle">
                  {fmtForUnit(key, baseline)}
                </td>
                <td className="border border-ink p-0 align-middle">
                  <div className="px-3 py-4 flex flex-col">
                    <div aria-hidden="true" style={{ height: 28 }} />
                    <input
                      type="text"
                      inputMode="numeric"
                      value={fmtForUnit(key, current)}
                      onChange={(e) => {
                        const parsed = parseForUnit(key, e.target.value);
                        if (parsed !== null) setLikely(key, parsed);
                      }}
                      className="w-full text-sm font-bold font-mono text-input-blue bg-canvas text-right rounded ring-2 ring-input-blue/40 px-2 py-1 focus:outline-none focus:ring-input-blue"
                    />
                    <div style={{ height: 12 }} />
                    <Slider.Root
                      className="relative flex items-center w-full h-4 select-none touch-none"
                      min={INPUT_META[key].bound[0]}
                      max={INPUT_META[key].bound[1]}
                      step={INPUT_META[key].step}
                      value={[current]}
                      onValueChange={([v]) => setLikely(key, v)}
                    >
                      <Slider.Track className="bg-button-grey relative grow rounded-full h-1">
                        <Slider.Range className="absolute bg-dial-grey rounded-full h-full" />
                      </Slider.Track>
                      <Slider.Thumb className="block w-3 h-3 bg-dial-grey border border-ink rounded-full focus:outline-none focus:ring-2 focus:ring-dial-grey/40" />
                    </Slider.Root>
                  </div>
                </td>
                <td className="border border-ink px-3 py-4 text-sm text-ink align-middle">
                  {unit}
                </td>
                <td className="border border-ink p-0 align-middle">
                  <textarea
                    value={rationales[key]}
                    onChange={(e) => setRationale(key, e.target.value)}
                    placeholder="enter rationale"
                    rows={1}
                    style={{ maxHeight: "7.5em" }}
                    className="w-full px-3 py-4 text-sm font-bold text-input-blue bg-canvas placeholder:font-normal placeholder:text-ink/40 focus:outline-none focus:ring-2 focus:ring-input-blue/40 resize-none overflow-y-auto block leading-snug"
                  />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
