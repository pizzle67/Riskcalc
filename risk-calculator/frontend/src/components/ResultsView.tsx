import { useState } from "react";
import { SimResult, useStore } from "../lib/state";
import SummaryStats from "./SummaryStats";
import Histogram from "./Histogram";
import ExceedanceCurve from "./ExceedanceCurve";
import { computedMateriality } from "./MaterialityInput";

type Props = { result: SimResult };

export default function ResultsView({ result }: Props) {
  const [histHover, setHistHover] = useState<string | null>(null);
  const [exHover, setExHover] = useState<string | null>(null);
  const materiality = useStore((s) => s.materiality);
  const matValue = computedMateriality(materiality);

  const totalCount = result.histogram.counts.reduce((a, b) => a + b, 0);
  const exceedCount = result.histogram.counts.reduce(
    (acc, c, i) => acc + (result.histogram.bins[i] >= matValue ? c : 0),
    0
  );
  const probExceed = totalCount > 0 ? (exceedCount / totalCount) * 100 : 0;

  return (
    <div className="space-y-4">
      <SummaryStats
        summary={result.summary}
        iterations={result.iterations}
        materiality={matValue}
        probExceed={probExceed}
      />

      <div className="grid lg:grid-cols-[1fr_2fr] gap-4">
        <div className="rounded-xl border border-ink bg-canvas p-3 flex flex-col">
          <h4 className="text-sm font-semibold text-ink mb-2">
            Distribution insight
          </h4>
          <p className="text-sm text-ink flex-1">
            {histHover ?? "Hover over a bar to see how often that loss range appears in the simulation."}
          </p>
        </div>
        <div className="rounded-xl border border-ink bg-canvas p-3">
          <h3 className="text-sm font-semibold text-ink mb-2">
            Annualized Loss Expectancy distribution
          </h3>
          <Histogram
            counts={result.histogram.counts}
            bins={result.histogram.bins}
            materiality={matValue}
            onHover={setHistHover}
          />
        </div>
      </div>

      <div className="grid lg:grid-cols-[1fr_2fr] gap-4">
        <div className="rounded-xl border border-ink bg-canvas p-3 flex flex-col">
          <h4 className="text-sm font-semibold text-ink mb-2">
            Exceedance insight
          </h4>
          <p className="text-sm text-ink flex-1">
            {exHover ?? "Hover over the curve to see the probability of exceeding a given annual loss."}
          </p>
        </div>
        <div className="rounded-xl border border-ink bg-canvas p-3">
          <h3 className="text-sm font-semibold text-ink mb-2">
            Loss exceedance curve
          </h3>
          <ExceedanceCurve
            values={result.exceedance.values}
            probabilities={result.exceedance.probabilities}
            materiality={matValue}
            onHover={setExHover}
          />
        </div>
      </div>
    </div>
  );
}
