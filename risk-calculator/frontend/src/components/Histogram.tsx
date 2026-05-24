import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { fmtUsd, fmtUsdShort } from "../lib/compute";

type Props = {
  counts: number[];
  bins: number[];
  materiality?: number | null;
  onHover?: (text: string | null) => void;
  trialNoun?: string;
  valueLabel?: string;
  rangeNoun?: string;
};

export default function Histogram({
  counts,
  bins,
  materiality,
  onHover,
  trialNoun = "simulated years",
  valueLabel = "Loss",
  rangeNoun = "an annual loss",
}: Props) {
  const data = counts.map((c, i) => ({
    bin: (bins[i] + bins[i + 1]) / 2,
    binLow: bins[i],
    binHigh: bins[i + 1],
    count: c,
  }));
  const total = counts.reduce((a, b) => a + b, 0);

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart
        data={data}
        margin={{ top: 10, right: 10, bottom: 8, left: 8 }}
        onMouseMove={(s: any) => {
          if (s && s.activePayload && s.activePayload.length) {
            const d = s.activePayload[0].payload;
            const pct = total > 0 ? ((d.count / total) * 100).toFixed(1) : "0";
            onHover?.(
              `${pct} percent of ${trialNoun} produced ${rangeNoun} between ${fmtUsd(
                d.binLow
              )} and ${fmtUsd(d.binHigh)}.`
            );
          }
        }}
        onMouseLeave={() => onHover?.(null)}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="bin"
          tickFormatter={(v) => fmtUsdShort(v)}
          tick={{ fontSize: 13, fill: "#000" }}
          stroke="#000"
          minTickGap={48}
        />
        <YAxis tick={{ fontSize: 13, fill: "#000" }} stroke="#000" />
        <Tooltip
          formatter={(v: number) => v.toLocaleString()}
          labelFormatter={(v: number) => `${valueLabel}: ${fmtUsd(v)}`}
          contentStyle={{ fontSize: 11 }}
        />
        <Bar dataKey="count" fill="#1d4ed8" />
        {materiality && (
          <ReferenceLine
            x={materiality}
            stroke="#000"
            strokeDasharray="4 2"
            label={{ value: "materiality", position: "top", fill: "#000", fontSize: 10 }}
          />
        )}
      </BarChart>
    </ResponsiveContainer>
  );
}
