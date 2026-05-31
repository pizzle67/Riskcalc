import { useState } from "react";
import { DecisionGridResult, DecisionGridScenario } from "../lib/state";
import { fmtUsd, fmtUsdShort } from "../lib/compute";

const DEFAULT_PANEL_W = 340;
const DEFAULT_PANEL_H = 300;
const MARGINS = { top: 28, right: 12, bottom: 56, left: 56 };

export function npvColor(npv: number, absMax: number): string {
  if (absMax === 0) return "#ffffff";
  const t = Math.max(-1, Math.min(1, npv / absMax));
  if (t < 0) {
    const u = -t;
    const r = Math.round(200 + (1 - u) * 55);
    const g = Math.round((1 - u) * 255);
    const b = Math.round((1 - u) * 255);
    return `rgb(${r},${g},${b})`;
  }
  const r = Math.round((1 - t) * 255);
  const g = Math.round(200 + (1 - t) * 55);
  const b = Math.round((1 - t) * 255);
  return `rgb(${r},${g},${b})`;
}

type HoverState =
  | { scenario: string; cost: number; reduction: number; npv: number }
  | null;

export function Heatmap({
  title,
  scenarioKey,
  scenario,
  costAxis,
  reductionAxis,
  marker,
  absMax,
  onHover,
  panelW = DEFAULT_PANEL_W,
  panelH = DEFAULT_PANEL_H,
}: {
  title: string;
  scenarioKey: string;
  scenario: DecisionGridScenario;
  costAxis: number[];
  reductionAxis: number[];
  marker: { cost: number; reduction: number };
  absMax: number;
  onHover?: (h: HoverState) => void;
  panelW?: number;
  panelH?: number;
}) {
  const M = MARGINS;
  const PANEL_W = panelW;
  const PANEL_H = panelH;
  const PLOT_W = PANEL_W - M.left - M.right;
  const PLOT_H = PANEL_H - M.top - M.bottom;
  const nCost = costAxis.length;
  const nRed = reductionAxis.length;
  const cellW = PLOT_W / nCost;
  const cellH = PLOT_H / nRed;

  const xForCost = (cost: number) => {
    const denom = costAxis[nCost - 1] - costAxis[0] || 1;
    return M.left + ((cost - costAxis[0]) / denom) * PLOT_W;
  };
  const yForReduction = (red: number) => {
    const denom = reductionAxis[nRed - 1] - reductionAxis[0] || 1;
    return M.top + (1 - (red - reductionAxis[0]) / denom) * PLOT_H;
  };

  const markerClamped = {
    cost: Math.max(costAxis[0], Math.min(costAxis[nCost - 1], marker.cost)),
    reduction: Math.max(reductionAxis[0], Math.min(reductionAxis[nRed - 1], marker.reduction)),
  };

  return (
    <svg width={PANEL_W} height={PANEL_H} role="img" className="block">
      <text
        x={PANEL_W / 2}
        y={18}
        textAnchor="middle"
        fontSize="13"
        fontWeight="600"
        fill="#000"
      >
        {title}
      </text>

      {scenario.grid.map((row, ri) =>
        row.map((npv, ci) => (
          <rect
            key={`${ri}-${ci}`}
            x={M.left + ci * cellW}
            y={M.top + (nRed - 1 - ri) * cellH}
            width={cellW}
            height={cellH}
            fill={npvColor(npv, absMax)}
            stroke="#ffffff"
            strokeWidth={0.5}
            onMouseEnter={() =>
              onHover?.({
                scenario: scenarioKey,
                cost: costAxis[ci],
                reduction: reductionAxis[ri],
                npv,
              })
            }
            onMouseLeave={() => onHover?.(null)}
          />
        ))
      )}

      <rect
        x={M.left}
        y={M.top}
        width={PLOT_W}
        height={PLOT_H}
        fill="none"
        stroke="#000"
        strokeWidth={1}
      />

      <circle
        cx={xForCost(markerClamped.cost)}
        cy={yForReduction(markerClamped.reduction)}
        r={6}
        fill="none"
        stroke="#000"
        strokeWidth={2}
      />
      <circle
        cx={xForCost(markerClamped.cost)}
        cy={yForReduction(markerClamped.reduction)}
        r={2}
        fill="#000"
      />

      <text x={M.left} y={M.top + PLOT_H + 14} fontSize="10" fill="#000" textAnchor="start">
        {fmtUsdShort(costAxis[0])}
      </text>
      <text x={M.left + PLOT_W} y={M.top + PLOT_H + 14} fontSize="10" fill="#000" textAnchor="end">
        {fmtUsdShort(costAxis[nCost - 1])}
      </text>
      <text x={M.left + PLOT_W / 2} y={M.top + PLOT_H + 32} fontSize="11" fill="#000" textAnchor="middle">
        Implementation Cost
      </text>

      <text x={M.left - 6} y={M.top + 4} fontSize="10" fill="#000" textAnchor="end">
        {Math.round(reductionAxis[nRed - 1] * 100)}%
      </text>
      <text x={M.left - 6} y={M.top + PLOT_H} fontSize="10" fill="#000" textAnchor="end">
        {Math.round(reductionAxis[0] * 100)}%
      </text>
      <text
        x={16}
        y={M.top + PLOT_H / 2}
        fontSize="11"
        fill="#000"
        textAnchor="middle"
        transform={`rotate(-90, 16, ${M.top + PLOT_H / 2})`}
      >
        Loss Reduction
      </text>
    </svg>
  );
}

export function ColorLegend({ absMax }: { absMax: number }) {
  const W = 320;
  const H = 36;
  const BAR_H = 12;
  const steps = 60;
  const cells = Array.from({ length: steps }, (_, i) => {
    const t = (i / (steps - 1)) * 2 - 1;
    return npvColor(t * absMax, absMax);
  });
  return (
    <svg width={W} height={H} role="img">
      {cells.map((c, i) => (
        <rect
          key={i}
          x={(i / steps) * W}
          y={0}
          width={W / steps + 0.5}
          height={BAR_H}
          fill={c}
        />
      ))}
      <rect x={0} y={0} width={W} height={BAR_H} fill="none" stroke="#000" strokeWidth={0.5} />
      <text x={0} y={BAR_H + 14} fontSize="10" fill="#000" textAnchor="start">
        {fmtUsd(-absMax)}
      </text>
      <text x={W / 2} y={BAR_H + 14} fontSize="10" fill="#000" textAnchor="middle">
        $0 (break-even)
      </text>
      <text x={W} y={BAR_H + 14} fontSize="10" fill="#000" textAnchor="end">
        {fmtUsd(absMax)}
      </text>
    </svg>
  );
}

type Props = { grid: DecisionGridResult };

export default function DecisionGrid({ grid }: Props) {
  const [hover, setHover] = useState<HoverState>(null);

  const allNpv = [
    ...grid.pessimistic.grid.flat(),
    ...grid.likely.grid.flat(),
    ...grid.optimistic.grid.flat(),
  ];
  const absMax = Math.max(1, ...allNpv.map((v) => Math.abs(v)));

  const scenarioLabel: Record<string, string> = {
    pessimistic: "Pessimistic case",
    likely: "Likely case",
    optimistic: "Optimistic case",
  };

  return (
    <div className="space-y-3">
      <div className="text-sm text-ink px-1">
        The grid shows the expected net present value of the proposed control
        across every combination of implementation cost and loss reduction
        within your three-point bounds. Green cells indicate a positive net
        present value; red cells indicate a negative one. The three panels
        cover an optimistic, central, and pessimistic combination of the
        other assumptions (baseline Annualized Loss Expectancy, ongoing
        operating cost, and discount rate). The black ring marks your most
        likely control settings.
      </div>

      <div className="grid lg:grid-cols-3 gap-3 justify-items-center">
        {(["pessimistic", "likely", "optimistic"] as const).map((key) => (
          <div
            key={key}
            className="rounded-xl border border-ink bg-canvas p-2"
          >
            <Heatmap
              title={scenarioLabel[key]}
              scenarioKey={key}
              scenario={grid[key]}
              costAxis={grid.costAxis}
              reductionAxis={grid.reductionAxis}
              marker={grid.marker}
              absMax={absMax}
              onHover={setHover}
            />
            <div className="text-[11px] text-ink/70 mt-1 px-2 leading-snug">
              Baseline loss: {fmtUsd(grid[key].baselineAle)} · Ongoing:{" "}
              {fmtUsd(grid[key].ongoingCost)} · Discount:{" "}
              {Math.round(grid[key].discountRate * 100)}%
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-start gap-6 px-1">
        <ColorLegend absMax={absMax} />
        <div className="text-sm text-ink flex-1">
          {hover ? (
            <>
              In the <strong>{scenarioLabel[hover.scenario].toLowerCase()}</strong>,
              spending <strong>{fmtUsd(hover.cost)}</strong> to achieve a{" "}
              <strong>{Math.round(hover.reduction * 100)}%</strong> loss reduction
              produces an expected net present value of{" "}
              <strong>{fmtUsd(hover.npv)}</strong> over {grid.horizonYears} years.
            </>
          ) : (
            "Hover over any cell to read off the expected net present value for that combination of implementation cost and loss reduction."
          )}
        </div>
      </div>
    </div>
  );
}
