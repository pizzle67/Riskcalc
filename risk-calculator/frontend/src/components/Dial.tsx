import * as Slider from "@radix-ui/react-slider";
import { Triangular } from "../lib/state";

type Props = {
  value: Triangular;
  baseline: Triangular;
  bound: [number, number];
  step: number;
  unit: string;
  onChange: (v: Triangular) => void;
  onReset: () => void;
};

const dialSize = 110;

export default function Dial({ value, baseline, bound, step, unit, onChange, onReset }: Props) {
  const [lo, hi] = bound;
  const span = Math.max(hi - lo, 1e-9);
  const angle = ((value.likely - lo) / span) * 270 - 135;
  const setKey = (key: keyof Triangular, v: number) =>
    onChange({ ...value, [key]: clamp(v, lo, hi) });

  return (
    <div className="flex flex-col items-center gap-3 p-1">
      <div className="grid grid-cols-3 gap-2 w-full text-[11px]">
        <NumField label="min"    value={value.min}    onChange={(v) => setKey("min",    v)} step={step} bound={bound} />
        <NumField label="likely" value={value.likely} onChange={(v) => setKey("likely", v)} step={step} bound={bound} highlight />
        <NumField label="max"    value={value.max}    onChange={(v) => setKey("max",    v)} step={step} bound={bound} />
      </div>

      <Slider.Root
        className="relative flex items-center w-full h-5"
        min={lo}
        max={hi}
        step={step}
        value={[value.likely]}
        onValueChange={([v]) => setKey("likely", v)}
      >
        <Slider.Track className="bg-button-grey relative grow rounded-full h-1.5">
          <Slider.Range className="absolute bg-input-blue rounded-full h-full" />
        </Slider.Track>
        <Slider.Thumb className="block w-4 h-4 bg-input-blue rounded-full focus:outline-none focus:ring-2 focus:ring-input-blue/40" />
      </Slider.Root>

      <div className="w-full text-[11px] flex items-center justify-between">
        <span className="text-ink">baseline likely: <b className="text-ink">{format(baseline.likely, unit)}</b></span>
        <button onClick={onReset} className="px-2 py-0.5 rounded border border-ink text-ink hover:bg-button-grey">
          reset
        </button>
      </div>
    </div>
  );
}

function NumField({
  label, value, onChange, step, bound, highlight,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  step: number;
  bound: [number, number];
  highlight?: boolean;
}) {
  return (
    <label className="flex flex-col text-ink">
      <span className="uppercase tracking-wide">{label}</span>
      <input
        type="number"
        value={value}
        step={step}
        min={bound[0]}
        max={bound[1]}
        onChange={(e) => onChange(parseFloat(e.target.value || "0"))}
        className={
          "border rounded px-1 py-0.5 text-ink bg-canvas " +
          (highlight ? "border-input-blue font-bold" : "border-ink")
        }
      />
    </label>
  );
}

function clamp(v: number, lo: number, hi: number) {
  return Math.min(hi, Math.max(lo, isFinite(v) ? v : lo));
}

function format(v: number, unit: string): string {
  if (unit === "USD") return `$${Math.round(v).toLocaleString("en-US")}`;
  if (unit === "probability" || unit === "0 to 1") return `${Math.round(v * 100)}%`;
  return `${Math.round(v)}`;
}
