import { ScenarioMetaKey, useStore } from "../lib/state";

const COLS: { key: ScenarioMetaKey; label: string; placeholder: string }[] = [
  { key: "scenarioNumber",  label: "Scenario Number", placeholder: "e.g. SCN-001" },
  { key: "asset",           label: "Asset",           placeholder: "e.g. Customer database" },
  { key: "threatCommunity", label: "Threat Community", placeholder: "e.g. Organized crime" },
  { key: "threatType",      label: "Threat Type",     placeholder: "e.g. Ransomware" },
  { key: "effect",          label: "Effect",          placeholder: "e.g. Confidentiality" },
];

type Props = { x: number; y: number; width: number };

export default function ScenarioTable({ x, y, width }: Props) {
  const meta = useStore((s) => s.scenarioMeta);
  const setMeta = useStore((s) => s.setScenarioMeta);

  return (
    <div
      className="absolute"
      style={{ left: x, top: y, width }}
    >
      <table className="w-full border-2 border-ink border-collapse table-fixed bg-canvas">
        <thead>
          <tr>
            {COLS.map((c) => (
              <th
                key={c.key}
                className="border border-ink px-2 py-1.5 text-[12px] font-semibold text-ink text-center bg-canvas"
              >
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            {COLS.map((c) => (
              <td key={c.key} className="border border-ink p-0">
                <input
                  type="text"
                  value={meta[c.key]}
                  onChange={(e) => setMeta(c.key, e.target.value)}
                  placeholder={c.placeholder}
                  className="w-full px-2 py-2 text-[13px] font-bold text-input-blue bg-canvas placeholder:font-normal placeholder:text-ink/40 focus:outline-none focus:ring-2 focus:ring-input-blue/40"
                />
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}
