import { useStore } from "../lib/state";
import {
  fmtCount,
  fmtPct,
  fmtUsd,
  rollupLef,
  rollupLm,
  rollupRisk,
  rollupSecondaryLoss,
  rollupTef,
  vulnerabilityFromGrid,
} from "../lib/compute";
import TreeNode from "./TreeNode";
import ScenarioTable from "./ScenarioTable";
import Toggle from "./Toggle";

const CANVAS_W = 1570;
const CANVAS_H = 740;
const COLLAPSED_H = 200;

const SCOPE_LABEL_Y = 8;
const TABLE = { x: 165, y: 44, width: 1240, height: 80 };
const TREE_LABEL_Y = 152;

const POS = {
  risk:    { x: 785,  y: 230 },
  lef:     { x: 460,  y: 360 },
  lm:      { x: 1110, y: 360 },
  tef:     { x: 215,  y: 500 },
  vuln:    { x: 705,  y: 500 },
  pl:      { x: 995,  y: 500 },
  sl:      { x: 1225, y: 500 },
  cf:      { x: 105,  y: 650 },
  poa:     { x: 325,  y: 650 },
  tc:      { x: 595,  y: 650 },
  rs:      { x: 815,  y: 650 },
  slef:    { x: 1115, y: 650 },
  slm:     { x: 1335, y: 650 },
} as const;

type Op = "x" | "+" | "MC";

const EDGES: { from: keyof typeof POS; to: keyof typeof POS }[] = [
  { from: "risk", to: "lef" },
  { from: "risk", to: "lm"  },
  { from: "lef",  to: "tef" },
  { from: "lef",  to: "vuln" },
  { from: "tef",  to: "cf"  },
  { from: "tef",  to: "poa" },
  { from: "vuln", to: "tc"  },
  { from: "vuln", to: "rs" },
  { from: "lm",   to: "pl"  },
  { from: "lm",   to: "sl" },
  { from: "sl",   to: "slef" },
  { from: "sl",   to: "slm" },
];

const SIBLING_OPS: { left: keyof typeof POS; right: keyof typeof POS; op: Op }[] = [
  { left: "lef",  right: "lm",   op: "x" },
  { left: "tef",  right: "vuln", op: "x" },
  { left: "cf",   right: "poa",  op: "x" },
  { left: "tc",   right: "rs",   op: "MC" },
  { left: "pl",   right: "sl",   op: "+" },
  { left: "slef", right: "slm",  op: "x" },
];

export default function FairTree() {
  const inputs = useStore((s) => s.inputs);
  const treeHidden = useStore((s) => s.treeHidden);
  const setTreeHidden = useStore((s) => s.setTreeHidden);

  const tef = rollupTef(inputs.contactFrequency, inputs.probabilityOfAction);
  const vuln = vulnerabilityFromGrid(inputs.threatCapability, inputs.resistanceStrength);
  const lef = rollupLef(tef, vuln);
  const sl = rollupSecondaryLoss(inputs.secondaryLossFrequency, inputs.secondaryLossMagnitude);
  const lm = rollupLm(inputs.primaryLoss, sl);
  const risk = rollupRisk(lef, lm);

  return (
    <div
      className="relative mx-auto"
      style={{ width: CANVAS_W, height: treeHidden ? COLLAPSED_H : CANVAS_H }}
    >
      {!treeHidden && (
      <svg
        className="absolute inset-0 pointer-events-none"
        width={CANVAS_W}
        height={CANVAS_H}
      >
        {EDGES.map((e, i) => {
          const a = POS[e.from];
          const b = POS[e.to];
          const midY = (a.y + b.y) / 2;
          const halfH = (k: keyof typeof POS) => (k === "risk" ? 30 : 40);
          const d = `M ${a.x} ${a.y + halfH(e.from)} C ${a.x} ${midY}, ${b.x} ${midY}, ${b.x} ${b.y - halfH(e.to)}`;
          return (
            <path
              key={i}
              d={d}
              stroke="#000000"
              strokeWidth="1.5"
              fill="none"
            />
          );
        })}
        {SIBLING_OPS.map((s, i) => {
          const a = POS[s.left];
          const b = POS[s.right];
          const cx = (a.x + b.x) / 2;
          const cy = (a.y + b.y) / 2;
          const isMc = s.op === "MC";
          const w = isMc ? 32 : 24;
          const h = 24;
          return (
            <g key={i} transform={`translate(${cx - w / 2},${cy - h / 2})`}>
              <rect width={w} height={h} rx="4" fill="#ffffff" stroke="#000000" />
              <text
                x={w / 2}
                y={16}
                textAnchor="middle"
                fontSize={isMc ? 10 : 14}
                fontWeight="700"
                fill="#000000"
              >
                {s.op === "x" ? "×" : s.op}
              </text>
            </g>
          );
        })}
      </svg>
      )}

      <div
        className="absolute text-base font-semibold text-ink whitespace-nowrap -translate-x-1/2"
        style={{ top: SCOPE_LABEL_Y, left: TABLE.x + TABLE.width / 2 }}
      >
        Scope Table
      </div>

      <ScenarioTable x={TABLE.x} y={TABLE.y} width={TABLE.width} />

      <div
        className="absolute"
        style={{ top: TREE_LABEL_Y - 2, left: TABLE.x + 20 }}
      >
        <Toggle
          label="Hide tree"
          on={treeHidden}
          onChange={(v) => setTreeHidden(v)}
        />
      </div>

      {!treeHidden && (
        <div
          className="absolute text-base font-semibold text-ink whitespace-nowrap -translate-x-1/2"
          style={{ top: TREE_LABEL_Y, left: POS.risk.x }}
        >
          Factor Analysis Tree
        </div>
      )}

      {!treeHidden && (
        <>
          <TreeNode title="Risk"                   kind="root"   {...POS.risk} width={220} height={60} rollup={fmtUsd(risk) + " / yr"} />
          <TreeNode title="Loss Event Frequency"   kind="branch" {...POS.lef}  rollup={fmtCount(lef) + " / yr"} />
          <TreeNode title="Loss Event Magnitude"   kind="branch" {...POS.lm}   rollup={fmtUsd(lm)} />
          <TreeNode title="Threat Event Frequency" kind="branch" {...POS.tef}  rollup={fmtCount(tef) + " / yr"} />
          <TreeNode title="Vulnerability"          kind="branch" {...POS.vuln} rollup={fmtPct(vuln)} />
          <TreeNode title="Primary Loss"           kind="leaf"   inputKey="primaryLoss"            {...POS.pl}  rollup={fmtUsd(inputs.primaryLoss.likely)} />
          <TreeNode title="Secondary Loss"         kind="branch" {...POS.sl}   rollup={fmtUsd(sl)} />
          <TreeNode title="Contact Frequency"      kind="leaf"   inputKey="contactFrequency"       {...POS.cf}  rollup={fmtCount(inputs.contactFrequency.likely) + " / yr"} />
          <TreeNode title="Probability of Action"  kind="leaf"   inputKey="probabilityOfAction"    {...POS.poa} rollup={fmtPct(inputs.probabilityOfAction.likely)} />
          <TreeNode title="Threat Capability"      kind="leaf"   inputKey="threatCapability"       {...POS.tc}  rollup={fmtPct(inputs.threatCapability.likely)} />
          <TreeNode title="Resistance Strength"    kind="leaf"   inputKey="resistanceStrength"     {...POS.rs}  rollup={fmtPct(inputs.resistanceStrength.likely)} />
          <TreeNode title="Sec. Loss Frequency"    kind="leaf"   inputKey="secondaryLossFrequency" {...POS.slef} rollup={fmtPct(inputs.secondaryLossFrequency.likely)} />
          <TreeNode title="Sec. Loss Magnitude"    kind="leaf"   inputKey="secondaryLossMagnitude" {...POS.slm}  rollup={fmtUsd(inputs.secondaryLossMagnitude.likely)} />

          <div
            className="absolute text-[11px] italic text-ink"
            style={{ left: 20, bottom: 12 }}
          >
            *Open FAIR<sup className="text-[7px] relative -top-1 ml-px">TM</sup> is a trademark of the Open Group
          </div>
        </>
      )}
    </div>
  );
}
