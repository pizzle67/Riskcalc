import { useState } from "react";
import { DecisionResult, useStore } from "../lib/state";
import { fmtUsd } from "../lib/compute";
import Histogram from "./Histogram";
import ExceedanceCurve from "./ExceedanceCurve";
import Tornado from "./Tornado";
import DecisionGrid from "./DecisionGrid";

type Props = { result: DecisionResult };

export default function DecisionResults({ result }: Props) {
  const [histHover, setHistHover] = useState<string | null>(null);
  const [exHover, setExHover] = useState<string | null>(null);
  const [tornadoHover, setTornadoHover] = useState<string | null>(null);
  const grid = useStore((s) => s.decisionGrid);

  const s = result.summary;
  const rows: [string, number][] = [
    ["Mean Net Present Value", s.mean],
    ["Median Net Present Value", s.median],
    ["Standard deviation", s.std],
    ["10th percentile", s.p10],
    ["90th percentile", s.p90],
    ["5th percentile (worst-case 5%)", s.var_95],
    ["Conditional shortfall (worst 5% mean)", s.cvar_95],
  ];

  return (
    <div className="flex flex-col gap-4">
      <div className="text-sm font-bold text-ink px-1 print:order-1">
        Over {result.horizonYears} years, the proposed control produces an
        average net present value of{" "}
        <span className="text-ink">{fmtUsd(s.mean)}</span>, with a{" "}
        {result.probPositive.toFixed(1)} percent chance of producing a positive
        net present value. The worst five percent of trials average{" "}
        <span className="text-ink">{fmtUsd(s.cvar_95)}</span>. Expected baseline
        annual loss is <span className="text-ink">{fmtUsd(result.expectedBaselineAle)}</span>;
        expected annual savings under the control are{" "}
        <span className="text-ink">{fmtUsd(result.expectedAnnualSavings)}</span>.
        The cancellation flag fired in {result.probCancelled.toFixed(1)} percent
        of trials. Results are based on {result.iterations.toLocaleString()} Monte
        Carlo iterations.
      </div>

      <table className="w-full border-collapse border-2 border-ink table-fixed bg-canvas print:order-2">
        <thead>
          <tr>
            {rows.map(([label]) => (
              <th
                key={label}
                className="border border-ink px-2 py-2 text-sm font-bold text-ink bg-panel-grey text-center leading-tight"
              >
                {label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            {rows.map(([label, value]) => (
              <td
                key={label}
                className="border border-ink px-2 py-2 text-sm font-bold text-ink text-center"
              >
                {fmtUsd(value)}
              </td>
            ))}
          </tr>
        </tbody>
      </table>

      <div className="grid lg:grid-cols-[1fr_2fr] gap-4 print:grid-cols-1 print-keep-together print:order-4">
        <div className="rounded-xl border border-ink bg-canvas p-3 flex flex-col print:hidden">
          <h4 className="text-sm font-semibold text-ink mb-2">
            Distribution insight
          </h4>
          <p className="text-sm text-ink flex-1">
            {histHover ??
              "Hover over a bar to see how often that net present value range appears in the simulation."}
          </p>
        </div>
        <div className="rounded-xl border border-ink bg-canvas p-3">
          <h3 className="text-sm font-semibold text-ink mb-2">
            Net present value distribution
          </h3>
          <Histogram
            counts={result.histogram.counts}
            bins={result.histogram.bins}
            materiality={0}
            onHover={setHistHover}
            trialNoun="trials"
            valueLabel="Net present value"
            rangeNoun="a net present value"
          />
        </div>
      </div>

      <div className="grid lg:grid-cols-[1fr_2fr] gap-4 print:grid-cols-1 print-keep-together print:order-5">
        <div className="rounded-xl border border-ink bg-canvas p-3 flex flex-col print:hidden">
          <h4 className="text-sm font-semibold text-ink mb-2">
            Exceedance insight
          </h4>
          <p className="text-sm text-ink flex-1">
            {exHover ??
              "Hover over the curve to see the probability of achieving at least a given net present value."}
          </p>
        </div>
        <div className="rounded-xl border border-ink bg-canvas p-3">
          <h3 className="text-sm font-semibold text-ink mb-2">
            Net present value exceedance curve
          </h3>
          <ExceedanceCurve
            values={result.exceedance.values}
            probabilities={result.exceedance.probabilities}
            materiality={0}
            onHover={setExHover}
            hoverTemplate={(prob, value) =>
              `There is a ${prob.toFixed(
                1
              )} percent chance that the net present value exceeds ${fmtUsd(value)}.`
            }
            tooltipLabel={(v) => `Net present value ≥ ${fmtUsd(v)}`}
          />
        </div>
      </div>

      {result.tornado && result.tornado.length > 0 && (
        <div className="grid lg:grid-cols-[1fr_2fr] gap-4 print:grid-cols-1 print-keep-together print:order-6">
          <div className="rounded-xl border border-ink bg-canvas p-3 flex flex-col print:hidden">
            <h4 className="text-sm font-semibold text-ink mb-2">
              Sensitivity insight
            </h4>
            <p className="text-sm text-ink flex-1">
              {tornadoHover ??
                "Hover over a bar to see which driver moves the net present value most and by how much."}
            </p>
          </div>
          <div className="rounded-xl border border-ink bg-canvas p-3">
            <Tornado
              rows={result.tornado}
              onHover={setTornadoHover}
              outcomeLabel="net present value"
            />
          </div>
        </div>
      )}

      {grid && (
        <div className="rounded-xl border border-ink bg-canvas p-3 print:order-3 print-keep-together">
          <h3 className="text-sm font-semibold text-ink mb-3">
            Cost versus Reduction decision grid
          </h3>
          <DecisionGrid grid={grid} />
        </div>
      )}
    </div>
  );
}
