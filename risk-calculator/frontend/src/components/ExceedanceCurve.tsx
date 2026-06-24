import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { fmtUsd, fmtUsdShort } from "../lib/compute";

type Props = {
  values: number[];
  probabilities: number[];
  materiality?: number | null;
};

export default function ExceedanceCurve({ values, probabilities, materiality }: Props) {
  const data = values.map((v, i) => ({ value: v, prob: probabilities[i] }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 8, right: 8, bottom: 4, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="value"
          tickFormatter={(v) => fmtUsdShort(v)}
          tick={{ fontSize: 10, fill: "#000" }}
          stroke="#9ca3af"
        />
        <YAxis
          tickFormatter={(v) => `${v.toFixed(0)}%`}
          tick={{ fontSize: 10, fill: "#000" }}
          stroke="#9ca3af"
        />
        <Tooltip
          formatter={(v: number) => `${v.toFixed(1)}%`}
          labelFormatter={(v: number) => `Loss ≥ ${fmtUsd(v)}`}
          contentStyle={{ fontSize: 11 }}
        />
        <Line
          dataKey="prob"
          type="monotone"
          stroke="#1d4ed8"
          strokeWidth={2}
          dot={false}
        />
        {materiality && (
          <ReferenceLine
            x={materiality}
            stroke="#000"
            strokeDasharray="4 2"
            label={{ value: "materiality", position: "top", fill: "#000", fontSize: 10 }}
          />
        )}
      </LineChart>
    </ResponsiveContainer>
  );
}
