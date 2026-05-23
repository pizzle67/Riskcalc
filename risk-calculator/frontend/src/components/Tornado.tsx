import * as Popover from "@radix-ui/react-popover";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { TornadoRow } from "../lib/api";
import citationsRaw from "../data/citations.json";

type Citation = { id: string; apa: string; url: string };
const CITES: Record<string, Citation> = citationsRaw as any;

const METHODOLOGY_IDS = ["iman-helton-1988", "marino-2008"];
const CONTEXT_IDS = [
  "eschenbach-1992",
  "borgonovo-plischke-2016",
  "borgonovo-rabitti-2023",
];

type Props = { rows: TornadoRow[]; onHover?: (text: string | null) => void };

export default function Tornado({ rows, onHover }: Props) {
  const data = rows.map((r) => ({
    input: r.input,
    rho: r.rho,
    absRho: Math.abs(r.rho),
    direction: r.rho >= 0 ? "positive" : "negative",
  }));

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-ink">
          Tornado sensitivity{" "}
          <Popover.Root>
            <Popover.Trigger asChild>
              <button
                type="button"
                className="text-input-blue underline hover:no-underline font-normal text-sm"
              >
                (methodology)
              </button>
            </Popover.Trigger>
            <Popover.Portal>
              <Popover.Content
                side="bottom"
                align="start"
                sideOffset={6}
                className="z-50 w-[520px] rounded-xl border-2 border-ink bg-canvas p-4 shadow-xl text-xs text-ink"
              >
                <div className="font-semibold mb-2 text-sm">
                  Methodology in plain language
                </div>
                <ol className="space-y-1.5 list-decimal pl-5 mb-3">
                  <li>
                    We run thousands of "what if" trials, sampling all seven
                    inputs randomly within their distributions.
                  </li>
                  <li>
                    For each trial, we compute the resulting annualized loss.
                  </li>
                  <li>
                    For each input, we measure how closely its values move with
                    the loss across all trials.
                  </li>
                  <li>
                    We rank inputs from the strongest driver of loss to the
                    weakest, longest bar to shortest.
                  </li>
                </ol>
                <div className="mb-2">
                  Statistical technique: Spearman rank correlation, a
                  non-parametric measure that captures monotonic relationships
                  without assuming linearity.
                </div>
                <div className="font-semibold mb-1">References on rank correlation for sensitivity analysis</div>
                <div className="text-[11px] mb-1 italic">
                  Disclosure: these papers document rank correlation methods
                  for sensitivity ranking, but do not specifically prescribe
                  the tornado chart as the output visualization. The
                  combination of rank correlation plus tornado bars is
                  practitioner convention, not a single peer-reviewed
                  methodology.
                </div>
                <ol className="space-y-1.5 list-decimal pl-5 mb-3">
                  {METHODOLOGY_IDS.map((id) => {
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
                <div className="font-semibold mb-1">
                  For more context on tornado charts
                </div>
                <ol className="space-y-1.5 list-decimal pl-5 mb-2">
                  {CONTEXT_IDS.map((id) => {
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
        </h3>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 10, right: 10, bottom: 10, left: 110 }}
          onMouseMove={(s: any) => {
            if (s && s.activePayload && s.activePayload.length) {
              const d = s.activePayload[0].payload;
              const direction = d.direction === "positive" ? "increases" : "decreases";
              onHover?.(
                `When ${d.input} goes up, the annualized loss ${direction}. Strength of relationship: ${d.absRho.toFixed(
                  2
                )} (rank correlation, where 1 is strongest).`
              );
            }
          }}
          onMouseLeave={() => onHover?.(null)}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            type="number"
            domain={[0, 1]}
            tick={{ fontSize: 12, fill: "#000" }}
            stroke="#000"
          />
          <YAxis
            type="category"
            dataKey="input"
            tick={{ fontSize: 12, fill: "#000" }}
            stroke="#000"
            width={110}
          />
          <Tooltip
            formatter={(v: number) => v.toFixed(2)}
            labelFormatter={(label) => `Input: ${label}`}
            contentStyle={{ fontSize: 11 }}
          />
          <Bar dataKey="absRho" isAnimationActive={false}>
            {data.map((d, i) => (
              <Cell key={i} fill={d.direction === "positive" ? "#1d4ed8" : "#9ca3af"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
