import citationsRaw from "../data/citations.json";
import sectorsRaw from "../data/sector_defaults.json";
import { useStore } from "../lib/state";

type Citation = { id: string; apa: string; url: string };

const CITATIONS: Citation[] = Object.values(citationsRaw) as Citation[];
const META: any = (sectorsRaw as any)._meta;

export default function References() {
  const open = useStore((s) => s.referencesOpen);
  const setOpen = useStore((s) => s.setReferencesOpen);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-ink/40 flex items-center justify-center p-6 no-print"
      onClick={() => setOpen(false)}
    >
      <div
        className="bg-canvas border-2 border-ink rounded-xl max-w-3xl w-full max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-5 py-3 border-b-2 border-ink flex items-center justify-between">
          <h2 className="text-lg font-bold text-ink">References</h2>
          <button
            onClick={() => setOpen(false)}
            className="px-3 py-1 bg-button-grey border border-ink rounded text-sm font-semibold text-ink"
          >
            Close
          </button>
        </div>
        <div className="px-5 py-4 space-y-3">
          <p className="text-xs italic text-ink">
            Data vintage: {META?.vintage ?? "n/a"}. {META?.disclaimer ?? ""}
          </p>
          <ol className="space-y-2 text-sm text-ink">
            {CITATIONS.sort((a, b) => a.apa.localeCompare(b.apa)).map((c) => (
              <li key={c.id} className="leading-snug">
                <a
                  href={c.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline hover:no-underline"
                >
                  {c.apa}
                </a>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </div>
  );
}
