import { InputKey, ScenarioMetaKey, Triangular, useStore } from "../lib/state";
import sectorsRaw from "../data/sector_defaults.json";

type SectorEntry = {
  id: string;
  display_name: string;
  defaults: Record<InputKey, Triangular>;
};

const SECTORS: Record<string, SectorEntry> = Object.fromEntries(
  Object.entries(sectorsRaw)
    .filter(([k]) => !k.startsWith("_"))
    .map(([k, v]) => [k, v as SectorEntry])
);

type ScopeCol = { key: ScenarioMetaKey; label: string; placeholder: string };

const TEXT_COLS_BEFORE: ScopeCol[] = [
  { key: "scenarioNumber",  label: "Scenario Number", placeholder: "e.g. SCN-001" },
];

const TEXT_COLS_AFTER: ScopeCol[] = [
  { key: "asset",           label: "Asset",            placeholder: "e.g. Customer database" },
  { key: "threatCommunity", label: "Threat Community", placeholder: "e.g. Organized crime" },
  { key: "threatType",      label: "Threat Type",      placeholder: "e.g. Ransomware" },
  { key: "effect",          label: "Effect",           placeholder: "e.g. Confidentiality" },
];

type Props = { x: number; y: number; width: number };

export default function ScenarioTable({ x, y, width }: Props) {
  const meta = useStore((s) => s.scenarioMeta);
  const setMeta = useStore((s) => s.setScenarioMeta);
  const sector = useStore((s) => s.sector);
  const setSector = useStore((s) => s.setSector);
  const setReferencesOpen = useStore((s) => s.setReferencesOpen);

  const renderTextCell = (c: ScopeCol) => (
    <td key={c.key} className="border border-ink p-0">
      <input
        type="text"
        value={meta[c.key]}
        onChange={(e) => setMeta(c.key, e.target.value)}
        placeholder={c.placeholder}
        className="w-full px-2 py-2 text-[13px] font-bold text-input-blue bg-canvas placeholder:font-normal placeholder:text-ink/40 focus:outline-none focus:ring-2 focus:ring-input-blue/40"
      />
    </td>
  );

  const renderTextHeader = (c: ScopeCol) => (
    <th
      key={c.key}
      className="border border-ink px-2 py-1.5 text-[12px] font-semibold text-ink text-center bg-canvas"
    >
      {c.label}
    </th>
  );

  return (
    <div
      className="absolute"
      style={{ left: x, top: y, width }}
    >
      <table className="w-full border-2 border-ink border-collapse table-fixed bg-canvas">
        <thead>
          <tr>
            {TEXT_COLS_BEFORE.map(renderTextHeader)}
            <th className="border border-ink px-2 py-1.5 text-[12px] font-semibold text-ink text-center bg-canvas">
              Industry{" "}
              <button
                type="button"
                onClick={() => setReferencesOpen(true)}
                className="text-input-blue underline hover:no-underline"
              >
                (References)
              </button>
            </th>
            {TEXT_COLS_AFTER.map(renderTextHeader)}
          </tr>
        </thead>
        <tbody>
          <tr>
            {TEXT_COLS_BEFORE.map(renderTextCell)}
            <td className="border border-ink p-0">
              <select
                value={sector}
                onChange={(e) => {
                  const id = e.target.value;
                  if (id === "custom") {
                    setSector("custom", {} as Record<InputKey, Triangular>);
                    return;
                  }
                  const entry = SECTORS[id];
                  if (entry) setSector(id, entry.defaults);
                }}
                className="w-full px-2 py-2 text-[13px] font-bold text-input-blue bg-canvas focus:outline-none focus:ring-2 focus:ring-input-blue/40"
              >
                <option value="custom">— Custom —</option>
                {Object.values(SECTORS).map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.display_name}
                  </option>
                ))}
              </select>
            </td>
            {TEXT_COLS_AFTER.map(renderTextCell)}
          </tr>
        </tbody>
      </table>
    </div>
  );
}
