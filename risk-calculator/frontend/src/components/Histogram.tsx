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
};

export default function Histogram({ counts, bins, materiality }: Props) {
  const data = counts.map((c, i) => ({
    bin: (bins[i] + bins[i + 1]) / 2,
    count: c,
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 8, right: 8, bottom: 4, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="bin"
          tickFormatter={(v) => fmtUsdShort(v)}
          tick={{ fontSize: 10, fill: "#000" }}
          stroke="#9ca3af"
        />
        <YAxis tick={{ fontSize: 10, fill: "#000" }} stroke="#9ca3af" />
        <Tooltip
          formatter={(v: number) => v.toLocaleString()}
          labelFormatter={(v: number) => `Loss: ${fmtUsd(v)}`}
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
