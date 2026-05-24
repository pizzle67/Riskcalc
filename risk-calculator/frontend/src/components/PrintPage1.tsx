import { useStore } from "../lib/state";
import { fmtUsd } from "../lib/compute";
import { Heatmap, ColorLegend } from "./DecisionGrid";

function recommendationFor(probPositive: number): string {
  if (probPositive >= 60) return "APPROVE";
  if (probPositive >= 40) return "APPROVE WITH CONDITIONS";
  return "REJECT";
}

function todayLong(): string {
  return new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function Tile({
  label,
  value,
  sub,
  blank,
}: {
  label: string;
  value: string;
  sub?: string;
  blank?: boolean;
}) {
  return (
    <div className="border-2 border-ink rounded-lg p-4 bg-canvas">
      <div className="text-xs font-semibold uppercase tracking-wide text-ink/70">
        {label}
      </div>
      <div
        className={
          "text-3xl font-bold mt-1 leading-tight " +
          (blank ? "text-ink/30" : "text-ink")
        }
      >
        {value}
      </div>
      {sub && (
        <div className={"text-xs mt-1 " + (blank ? "text-ink/30" : "text-ink/70")}>
          {sub}
        </div>
      )}
    </div>
  );
}

export default function PrintPage1() {
  const result = useStore((s) => s.decisionResult);
  const grid = useStore((s) => s.decisionGrid);
  const meta = useStore((s) => s.scenarioMeta);
  const oneLiner = useStore((s) => s.scenarioOneLiner);

  const hasResult = result !== null;
  const hasGrid = grid !== null;

  const allNpv = hasGrid
    ? [
        ...grid!.pessimistic.grid.flat(),
        ...grid!.likely.grid.flat(),
        ...grid!.optimistic.grid.flat(),
      ]
    : [];
  const absMax = hasGrid ? Math.max(1, ...allNpv.map((v) => Math.abs(v))) : 1;

  const scenarioLabel: Record<string, string> = {
    pessimistic: "Pessimistic case",
    likely: "Likely case",
    optimistic: "Optimistic case",
  };

  return (
    <div className="print-section">
      {/* Header strip: scenario number + one-liner replaces the FAIR header */}
      <div className="flex items-baseline justify-between border-b-2 border-ink pb-1 mb-3 text-xs text-ink">
        <span className="font-semibold">
          {meta.scenarioNumber || "Scenario —"}
          {oneLiner ? ` · ${oneLiner}` : ""}
        </span>
        <span className="text-ink/70">{todayLong()}</span>
      </div>

      {/* Title block */}
      <div className="text-center mb-3">
        <h1 className="text-2xl font-bold text-ink tracking-tight">
          Decision Analysis Report
        </h1>
        {oneLiner && (
          <div className="text-sm font-semibold text-ink mt-1">{oneLiner}</div>
        )}
      </div>

      {/* Three NPV tiles */}
      <div
        className={
          "grid grid-cols-3 gap-3 mb-3 " +
          (hasResult ? "" : "print-watermark min-h-[120px]")
        }
      >
        <Tile
          label="Expected Net Present Value"
          value={hasResult ? fmtUsd(result!.summary.mean) : "—"}
          sub={
            hasResult
              ? `Median ${fmtUsd(result!.summary.median)}`
              : "Run decision analysis"
          }
          blank={!hasResult}
        />
        <Tile
          label="Probability of Positive Return"
          value={hasResult ? `${result!.probPositive.toFixed(1)}%` : "—"}
          sub={
            hasResult
              ? `Cancellation fired in ${result!.probCancelled.toFixed(1)}% of trials`
              : "Run decision analysis"
          }
          blank={!hasResult}
        />
        <Tile
          label="Recommendation"
          value={hasResult ? recommendationFor(result!.probPositive) : "—"}
          sub={
            hasResult
              ? `Over ${result!.horizonYears}-year horizon`
              : "Run decision analysis"
          }
          blank={!hasResult}
        />
      </div>

      {/* Three heatmaps horizontally */}
      <div className="rounded-xl border border-ink bg-canvas p-2">
        <h3 className="text-sm font-semibold text-ink mb-2">
          Cost versus Reduction decision grid
        </h3>
        {hasGrid ? (
          <>
            <div className="grid grid-cols-3 gap-2 justify-items-center">
              {(["pessimistic", "likely", "optimistic"] as const).map((key) => (
                <div key={key}>
                  <Heatmap
                    title={scenarioLabel[key]}
                    scenarioKey={key}
                    scenario={grid![key]}
                    costAxis={grid!.costAxis}
                    reductionAxis={grid!.reductionAxis}
                    marker={grid!.marker}
                    absMax={absMax}
                    panelW={300}
                    panelH={260}
                  />
                  <div className="text-[10px] text-ink/70 mt-1 px-1 text-center leading-snug">
                    Baseline: {fmtUsd(grid![key].baselineAle)} · Ongoing:{" "}
                    {fmtUsd(grid![key].ongoingCost)} · Discount:{" "}
                    {Math.round(grid![key].discountRate * 100)}%
                  </div>
                </div>
              ))}
            </div>
            <div className="flex justify-center mt-2">
              <ColorLegend absMax={absMax} />
            </div>
          </>
        ) : (
          <div className="print-watermark min-h-[260px]" />
        )}
      </div>

      {/* Decision results narrative at the bottom */}
      {hasResult && (
        <p className="text-[11px] text-ink leading-relaxed mt-3 px-1">
          Over {result!.horizonYears} years, the proposed control produces an
          average net present value of{" "}
          <strong>{fmtUsd(result!.summary.mean)}</strong>, with a{" "}
          <strong>{result!.probPositive.toFixed(1)} percent</strong> chance of
          producing a positive net present value. The worst five percent of
          trials average <strong>{fmtUsd(result!.summary.cvar_95)}</strong>.
          Expected baseline annual loss is{" "}
          <strong>{fmtUsd(result!.expectedBaselineAle)}</strong>; expected
          annual savings under the control are{" "}
          <strong>{fmtUsd(result!.expectedAnnualSavings)}</strong>. The
          cancellation flag fired in{" "}
          <strong>{result!.probCancelled.toFixed(1)} percent</strong> of
          trials. Results are based on{" "}
          {result!.iterations.toLocaleString()} Monte Carlo iterations.
        </p>
      )}
    </div>
  );
}
