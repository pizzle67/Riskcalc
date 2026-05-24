import { Triangular, useStore } from "../lib/state";

type TriKey = "lossReduction" | "implementationCost" | "ongoingCost" | "discountRate";
type ScalarKey =
  | "cancellationProbability"
  | "horizonYears"
  | "rampUpYear"
  | "efficacyDecay"
  | "salvageValue"
  | "residualLossFloor";

type Unit = "percent" | "usd" | "years";

const TRI_ROWS: { key: TriKey; label: string; unit: Unit }[] = [
  { key: "lossReduction",      label: "Loss Reduction",       unit: "percent" },
  { key: "implementationCost", label: "Implementation Cost",  unit: "usd"     },
  { key: "ongoingCost",        label: "Ongoing Operating Cost", unit: "usd"   },
  { key: "discountRate",       label: "Discount Rate",        unit: "percent" },
];

const SCALAR_ROWS: { key: ScalarKey; label: string; unit: Unit }[] = [
  { key: "cancellationProbability", label: "Cancellation Probability", unit: "percent" },
  { key: "horizonYears",            label: "Time Horizon",             unit: "years"   },
  { key: "rampUpYear",              label: "Ramp-up Year",             unit: "years"   },
  { key: "efficacyDecay",           label: "Efficacy Decay per Year",  unit: "percent" },
  { key: "salvageValue",            label: "Salvage Value on Cancel",  unit: "usd"     },
  { key: "residualLossFloor",       label: "Residual Loss Floor per Year", unit: "usd" },
];

function fmt(unit: Unit, v: number): string {
  if (unit === "usd") return `$${Math.round(v).toLocaleString("en-US")}`;
  if (unit === "percent") return `${Math.round(v * 100)}%`;
  return `${Math.round(v)}`;
}

function parse(unit: Unit, str: string): number | null {
  const cleaned = str.replace(/[^0-9.-]/g, "");
  if (cleaned === "" || cleaned === "-") return 0;
  const n = parseFloat(cleaned);
  if (!Number.isFinite(n)) return null;
  return unit === "percent" ? n / 100 : n;
}

function TriangularRow({
  label,
  unit,
  value,
  onChange,
}: {
  label: string;
  unit: Unit;
  value: Triangular;
  onChange: (v: Triangular) => void;
}) {
  const update = (field: keyof Triangular, str: string) => {
    const parsed = parse(unit, str);
    if (parsed === null) return;
    onChange({ ...value, [field]: parsed });
  };
  const cell =
    "border border-ink p-0 align-middle";
  const input =
    "w-full text-sm font-bold font-mono text-input-blue bg-canvas text-right rounded ring-2 ring-input-blue/40 px-2 py-1 focus:outline-none focus:ring-input-blue";

  return (
    <tr className="border-b border-ink last:border-0">
      <td className="border border-ink px-3 py-3 text-sm text-ink align-middle">
        {label}
      </td>
      <td className={cell}>
        <div className="px-3 py-3">
          <input
            type="text"
            inputMode="numeric"
            value={fmt(unit, value.min)}
            onChange={(e) => update("min", e.target.value)}
            className={input}
          />
        </div>
      </td>
      <td className={cell}>
        <div className="px-3 py-3">
          <input
            type="text"
            inputMode="numeric"
            value={fmt(unit, value.likely)}
            onChange={(e) => update("likely", e.target.value)}
            className={input}
          />
        </div>
      </td>
      <td className={cell}>
        <div className="px-3 py-3">
          <input
            type="text"
            inputMode="numeric"
            value={fmt(unit, value.max)}
            onChange={(e) => update("max", e.target.value)}
            className={input}
          />
        </div>
      </td>
      <td className="border border-ink px-3 py-3 text-sm text-ink align-middle">
        {unit === "usd" ? "USD" : unit === "percent" ? "percent" : "years"}
      </td>
    </tr>
  );
}

function ScalarRow({
  label,
  unit,
  value,
  onChange,
}: {
  label: string;
  unit: Unit;
  value: number;
  onChange: (v: number) => void;
}) {
  return (
    <tr className="border-b border-ink last:border-0">
      <td className="border border-ink px-3 py-3 text-sm text-ink align-middle">
        {label}
      </td>
      <td className="border border-ink p-0 align-middle" colSpan={3}>
        <div className="px-3 py-3">
          <input
            type="text"
            inputMode="numeric"
            value={fmt(unit, value)}
            onChange={(e) => {
              const parsed = parse(unit, e.target.value);
              if (parsed !== null) onChange(parsed);
            }}
            className="w-full text-sm font-bold font-mono text-input-blue bg-canvas text-right rounded ring-2 ring-input-blue/40 px-2 py-1 focus:outline-none focus:ring-input-blue"
          />
        </div>
      </td>
      <td className="border border-ink px-3 py-3 text-sm text-ink align-middle">
        {unit === "usd" ? "USD" : unit === "percent" ? "percent" : "years"}
      </td>
    </tr>
  );
}

export default function DecisionInputs() {
  const di = useStore((s) => s.decisionInputs);
  const setTri = useStore((s) => s.setDecisionTriangular);
  const setScalar = useStore((s) => s.setDecisionScalar);

  const triValue = (key: TriKey): Triangular => di[key];
  const scalarValue = (key: ScalarKey): number => di[key] as number;

  const th =
    "border border-ink px-3 py-2 text-sm font-semibold text-ink bg-panel-grey leading-tight";

  return (
    <div className="space-y-4">
      <div className="text-sm text-ink">
        The decision analysis evaluates a proposed control against the baseline
        scenario configured on the Factor Analysis tab. Each trial samples a
        loss reduction, an implementation cost, an ongoing operating cost, and
        a discount rate, then computes the net present value of the avoided
        losses minus the control's cost over the time horizon. A cancellation
        flag is drawn per trial; cancelled trials forfeit benefits but recover
        the salvage value.
      </div>

      <div className="rounded-xl border-2 border-ink bg-canvas overflow-hidden">
        <table className="w-full border-collapse table-fixed">
          <thead>
            <tr>
              <th className={`${th} w-[280px]`}>Three-point Variable</th>
              <th className={th}>Minimum</th>
              <th className={th}>Most Likely</th>
              <th className={th}>Maximum</th>
              <th className={`${th} w-[120px]`}>Unit</th>
            </tr>
          </thead>
          <tbody>
            {TRI_ROWS.map(({ key, label, unit }) => (
              <TriangularRow
                key={key}
                label={label}
                unit={unit}
                value={triValue(key)}
                onChange={(v) => setTri(key, v)}
              />
            ))}
          </tbody>
        </table>
      </div>

      <div className="rounded-xl border-2 border-ink bg-canvas overflow-hidden">
        <table className="w-full border-collapse table-fixed">
          <thead>
            <tr>
              <th className={`${th} w-[280px]`}>Scalar Variable</th>
              <th className={th} colSpan={3}>Value</th>
              <th className={`${th} w-[120px]`}>Unit</th>
            </tr>
          </thead>
          <tbody>
            {SCALAR_ROWS.map(({ key, label, unit }) => (
              <ScalarRow
                key={key}
                label={label}
                unit={unit}
                value={scalarValue(key)}
                onChange={(v) => setScalar(key, v)}
              />
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}
