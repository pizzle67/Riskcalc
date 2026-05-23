import * as Popover from "@radix-ui/react-popover";
import { InputKey, Triangular, INPUT_META, useStore } from "../lib/state";
import Dial from "./Dial";

export type NodeKind = "root" | "branch" | "leaf";

type Props = {
  title: string;
  kind: NodeKind;
  inputKey?: InputKey;
  rollup?: string;
  x: number;
  y: number;
  width?: number;
  height?: number;
};

const DEFAULT_W = 170;
const DEFAULT_H = 80;

export default function TreeNode({ title, kind, inputKey, rollup, x, y, width, height }: Props) {
  const W = width ?? DEFAULT_W;
  const H = height ?? DEFAULT_H;
  const inputs = useStore((s) => s.inputs);
  const baselines = useStore((s) => s.baselines);
  const setLeaf = useStore((s) => s.setLeaf);
  const resetToBaseline = useStore((s) => s.resetToBaseline);

  const card = (
    <div
      className={
        "absolute select-none rounded-lg border-2 border-ink px-3 py-2 bg-canvas shadow-sm transition flex flex-col items-center justify-center text-center " +
        (kind === "leaf" ? "cursor-pointer hover:shadow-md" : "")
      }
      style={{ left: x - W / 2, top: y - H / 2, width: W, height: H }}
    >
      <div className="text-[13px] font-semibold leading-tight text-ink">{title}</div>
      {inputKey && (
        <div className="mt-1 text-[11px] text-ink">
          Baseline {formatBaseline(inputKey, baselines[inputKey])}
        </div>
      )}
      {rollup !== undefined && (
        <div className="mt-1 text-[12px] text-ink whitespace-nowrap">
          <span>Input Value: </span>
          <span className="font-mono font-bold text-input-pink">{rollup}</span>
        </div>
      )}
    </div>
  );

  if (kind !== "leaf" || !inputKey) return card;

  const meta = INPUT_META[inputKey];

  return (
    <Popover.Root>
      <Popover.Trigger asChild>{card}</Popover.Trigger>
      <Popover.Portal>
        <Popover.Content
          side="bottom"
          align="center"
          sideOffset={8}
          className="z-50 w-64 rounded-xl border border-ink bg-canvas p-4 shadow-xl"
        >
          <div className="mb-2">
            <div className="text-sm font-bold text-ink">{meta.label}</div>
            <div className="text-[11px] text-dial-grey">unit: {meta.unit}</div>
          </div>
          <Dial
            value={inputs[inputKey]}
            baseline={baselines[inputKey]}
            bound={meta.bound}
            step={meta.step}
            unit={meta.unit}
            onChange={(v: Triangular) => setLeaf(inputKey, v)}
            onReset={() => resetToBaseline(inputKey)}
          />
          <Popover.Arrow className="fill-ink" />
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );
}

function formatBaseline(key: InputKey, t: Triangular): string {
  const v = t.likely;
  if (key === "primaryLoss" || key === "secondaryLossMagnitude") {
    return `$${Math.round(v).toLocaleString("en-US")}`;
  }
  if (
    key === "probabilityOfAction" ||
    key === "threatCapability" ||
    key === "resistanceStrength" ||
    key === "secondaryLossFrequency"
  ) {
    return `${Math.round(v * 100)}%`;
  }
  return `${Math.round(v)}`;
}

export { DEFAULT_W as W, DEFAULT_H as H };
