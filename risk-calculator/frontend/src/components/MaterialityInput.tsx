import * as Popover from "@radix-ui/react-popover";
import { useStore } from "../lib/state";
import citationsRaw from "../data/citations.json";

type Citation = { id: string; apa: string; url: string };
const CITES: Record<string, Citation> = citationsRaw as any;

export const METRIC_OPTIONS: { value: "manual" | "market_cap" | "revenue" | "net_income"; label: string; defaultPct: number }[] = [
  { value: "manual",     label: "Manual",                defaultPct: 100 },
  { value: "market_cap", label: "Market Capitalization", defaultPct: 0.5 },
  { value: "revenue",    label: "Annual Revenue",        defaultPct: 1.0 },
  { value: "net_income", label: "Net Income",            defaultPct: 5.0 },
];

function fmtUsd(v: number): string {
  return `$${Math.round(v).toLocaleString("en-US")}`;
}

function parseInput(str: string): number | null {
  const cleaned = str.replace(/[^0-9.-]/g, "");
  if (cleaned === "" || cleaned === "-") return 0;
  const n = parseFloat(cleaned);
  return Number.isFinite(n) ? n : null;
}

export function computedMateriality(m: ReturnType<typeof useStore.getState>["materiality"]): number {
  if (m.metric === "manual") return m.value;
  return m.value * (m.threshold / 100);
}

const REFERENCED_IDS = ["sec-cyber-rule-2023", "sec-sab-99"];

export default function MaterialityInput() {
  const materiality = useStore((s) => s.materiality);
  const setMateriality = useStore((s) => s.setMateriality);

  const isManual = materiality.metric === "manual";
  const computed = computedMateriality(materiality);

  return (
    <table className="w-full border-2 border-ink border-collapse table-fixed bg-canvas">
      <thead>
        <tr>
          <th className="border border-ink px-2 py-1.5 text-[12px] font-semibold text-ink text-center bg-canvas">
            Materiality Basis{" "}
            <Popover.Root>
              <Popover.Trigger asChild>
                <button
                  type="button"
                  className="text-input-blue underline hover:no-underline font-normal"
                >
                  (references)
                </button>
              </Popover.Trigger>
              <Popover.Portal>
                <Popover.Content
                  side="bottom"
                  align="start"
                  sideOffset={6}
                  className="z-50 w-[420px] rounded-xl border-2 border-ink bg-canvas p-4 shadow-xl text-xs text-ink"
                >
                  <div className="font-semibold mb-2">References</div>
                  <ol className="space-y-2 list-decimal pl-4">
                    {REFERENCED_IDS.map((id) => {
                      const c = CITES[id];
                      if (!c) return null;
                      return (
                        <li key={id} className="leading-snug">
                          <a
                            href={c.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="underline hover:no-underline"
                          >
                            {c.apa}
                          </a>
                        </li>
                      );
                    })}
                  </ol>
                  <Popover.Arrow className="fill-ink" />
                </Popover.Content>
              </Popover.Portal>
            </Popover.Root>
          </th>
          <th className="border border-ink px-2 py-1.5 text-[12px] font-semibold text-ink text-center bg-canvas">
            Reference Value
          </th>
          <th className="border border-ink px-2 py-1.5 text-[12px] font-semibold text-ink text-center bg-canvas">
            Percent Threshold
          </th>
          <th className="border border-ink px-2 py-1.5 text-[12px] font-semibold text-ink text-center bg-canvas">
            Computed Materiality
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td className="border border-ink p-0">
            <select
              value={materiality.metric}
              onChange={(e) => {
                const m = e.target.value as typeof materiality.metric;
                const found = METRIC_OPTIONS.find((o) => o.value === m);
                setMateriality({ metric: m, threshold: found?.defaultPct ?? materiality.threshold });
              }}
              className="w-full px-2 py-2 text-[13px] font-bold text-input-blue bg-canvas focus:outline-none focus:ring-2 focus:ring-input-blue/40"
            >
              {METRIC_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </td>
          <td className="border border-ink p-0">
            <input
              type="text"
              inputMode="numeric"
              value={fmtUsd(materiality.value)}
              onChange={(e) => {
                const v = parseInput(e.target.value);
                if (v !== null) setMateriality({ value: v });
              }}
              className="w-full px-2 py-2 text-[13px] font-bold text-input-blue bg-canvas text-center focus:outline-none focus:ring-2 focus:ring-input-blue/40"
            />
          </td>
          <td className="border border-ink p-0">
            {isManual ? (
              <div className="w-full px-2 py-2 text-[13px] text-ink text-center">—</div>
            ) : (
              <input
                type="text"
                inputMode="decimal"
                value={`${materiality.threshold}%`}
                onChange={(e) => {
                  const cleaned = e.target.value.replace(/[^0-9.]/g, "");
                  const v = parseFloat(cleaned);
                  if (Number.isFinite(v)) setMateriality({ threshold: v });
                  else if (cleaned === "") setMateriality({ threshold: 0 });
                }}
                className="w-full px-2 py-2 text-[13px] font-bold text-input-blue bg-canvas text-center focus:outline-none focus:ring-2 focus:ring-input-blue/40"
              />
            )}
          </td>
          <td className="border border-ink px-2 py-2 text-[13px] font-bold text-input-pink text-center">
            {fmtUsd(computed)}
          </td>
        </tr>
      </tbody>
    </table>
  );
}
