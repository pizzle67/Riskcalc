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
  onHover?: (text: string | null) => void;
};

export default function ExceedanceCurve({ values, probabilities, materiality, onHover }: Props) {
  const data = values.map((v, i) => ({ value: v, prob: probabilities[i] }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart
        data={data}
        margin={{ top: 10, right: 10, bottom: 8, left: 8 }}
        onMouseMove={(s: any) => {
          if (s && s.activePayload && s.activePayload.length) {
            const d = s.activePayload[0].payload;
            onHover?.(
              `There is a ${d.prob.toFixed(
                1
              )} percent chance that annual losses will exceed ${fmtUsd(d.value)}.`
            );
          }
        }}
        onMouseLeave={() => onHover?.(null)}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="value"
          tickFormatter={(v) => fmtUsdShort(v)}
          tick={{ fontSize: 13, fill: "#000" }}
          stroke="#000"
          minTickGap={60}
        />
        <YAxis
          tickFormatter={(v) => `${v.toFixed(0)}%`}
          tick={{ fontSize: 13, fill: "#000" }}
          stroke="#000"
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
