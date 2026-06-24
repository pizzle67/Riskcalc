import { useEffect, useState } from "react";
import FairTree from "./components/FairTree";
import InputTable from "./components/InputTable";
import Toggle from "./components/Toggle";
import ScenarioSummary from "./components/ScenarioSummary";
import Histogram from "./components/Histogram";
import ExceedanceCurve from "./components/ExceedanceCurve";
import SummaryStats from "./components/SummaryStats";
import { useStore } from "./lib/state";

export default function App() {
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const tableFrozen = useStore((s) => s.tableFrozen);
  const setTableFrozen = useStore((s) => s.setTableFrozen);
  const result = useStore((s) => s.result);

  useEffect(() => {
    fetch("/api/scenarios")
      .then((r) => setBackendOk(r.ok))
      .catch(() => setBackendOk(false));
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-canvas">
      <header className="border-b border-ink px-6 py-4 flex items-center justify-between bg-canvas">
        <div className="flex items-baseline gap-3">
          <h1 className="text-xl font-bold text-ink tracking-tight">
            FAIR<sup className="text-[6px] font-semibold relative -top-2.5 ml-px">TM</sup> Risk Calculator
          </h1>
          <span className="text-xs text-ink">
            Factor Analysis of Information Risk
          </span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <button
            onClick={() => window.print()}
            className="no-print px-3 py-1 bg-button-grey border border-ink rounded text-sm font-semibold text-ink hover:brightness-95"
          >
            Generate PDF
          </button>
          <span className="text-ink">backend</span>
          <span
            className={
              "px-2 py-0.5 rounded-full text-xs font-semibold " +
              (backendOk === null
                ? "bg-button-grey text-ink"
                : backendOk
                ? "bg-input-blue text-canvas"
                : "bg-red-100 text-red-700")
            }
          >
            {backendOk === null ? "checking" : backendOk ? "connected" : "offline"}
          </span>
        </div>
      </header>

      <main className="flex-1 flex flex-col">
        <section className="border-b border-ink p-6 overflow-auto bg-canvas">
          <div className="rounded-xl border border-ink bg-canvas p-4 overflow-auto">
            <FairTree />
          </div>
        </section>

        <section className="border-b border-ink p-6 overflow-auto bg-canvas">
          <div className="relative">
            <h2 className="text-base font-semibold text-ink mb-4 text-center">
              Input Table
            </h2>
            <div
              className="absolute top-0 -translate-x-1/2 z-10"
              style={{ left: 64 }}
            >
              <Toggle
                label="Freeze table"
                on={tableFrozen}
                onChange={(v) => setTableFrozen(v)}
              />
            </div>
            <InputTable />
          </div>
        </section>

        <section className="border-b border-ink p-6 overflow-auto bg-canvas">
          <h2 className="text-base font-semibold text-ink mb-4 text-center">
            Scenario Summary
          </h2>
          <ScenarioSummary />
        </section>

        <section className="p-6 bg-panel-grey/40">
          <h2 className="text-base font-semibold text-ink mb-4">Results</h2>
          {result ? (
            <div className="space-y-4">
              <SummaryStats summary={result.summary} iterations={result.iterations} />
              <div className="grid lg:grid-cols-2 gap-4">
                <div className="rounded-xl border border-ink bg-canvas p-3">
                  <h3 className="text-sm font-semibold text-ink mb-2">
                    Annualized Loss Expectancy distribution
                  </h3>
                  <Histogram
                    counts={result.histogram.counts}
                    bins={result.histogram.bins}
                  />
                </div>
                <div className="rounded-xl border border-ink bg-canvas p-3">
                  <h3 className="text-sm font-semibold text-ink mb-2">
                    Loss exceedance curve
                  </h3>
                  <ExceedanceCurve
                    values={result.exceedance.values}
                    probabilities={result.exceedance.probabilities}
                  />
                </div>
              </div>
            </div>
          ) : (
            <div className="rounded-xl border border-ink bg-canvas h-[300px] flex items-center justify-center text-ink text-sm">
              Click Run Scenario to see the distribution and statistics
            </div>
          )}
        </section>
      </main>

      <footer className="border-t border-ink px-6 py-3 text-xs text-ink">
        scaffold v0.1 · tree wired · dials live · simulation next
      </footer>
    </div>
  );
}
