import { useEffect, useState } from "react";
import FairTree from "./components/FairTree";
import InputTable from "./components/InputTable";
import Toggle from "./components/Toggle";
import ScenarioSummary from "./components/ScenarioSummary";
import ResultsView from "./components/ResultsView";
import References from "./components/References";
import DecisionInputs from "./components/DecisionInputs";
import DecisionResults from "./components/DecisionResults";
import PrintPage1 from "./components/PrintPage1";
import PrintPage2 from "./components/PrintPage2";
import PrintPage3 from "./components/PrintPage3";
import PrintAppendix from "./components/PrintAppendix";
import { useStore } from "./lib/state";
import { simulate, tornado, decision, decisionGrid } from "./lib/api";

export default function App() {
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const tableFrozen = useStore((s) => s.tableFrozen);
  const setTableFrozen = useStore((s) => s.setTableFrozen);
  const result = useStore((s) => s.result);
  const activeTab = useStore((s) => s.activeTab);
  const setActiveTab = useStore((s) => s.setActiveTab);
  const decisionResult = useStore((s) => s.decisionResult);

  // Wired here so a single header button can drive whichever tab is active.
  const inputs = useStore((s) => s.inputs);
  const iterations = useStore((s) => s.iterations);
  const di = useStore((s) => s.decisionInputs);
  const setResult = useStore((s) => s.setResult);
  const setTornado = useStore((s) => s.setTornado);
  const setDecisionResult = useStore((s) => s.setDecisionResult);
  const setDecisionGrid = useStore((s) => s.setDecisionGrid);
  const running = useStore((s) => s.running);
  const setRunning = useStore((s) => s.setRunning);
  const decisionRunning = useStore((s) => s.decisionRunning);
  const setDecisionRunning = useStore((s) => s.setDecisionRunning);

  useEffect(() => {
    fetch("/api/scenarios")
      .then((r) => setBackendOk(r.ok))
      .catch(() => setBackendOk(false));
  }, []);

  const runFactor = async () => {
    setRunning(true);
    try {
      const [r, t] = await Promise.all([
        simulate(inputs, iterations),
        tornado(inputs, iterations),
      ]);
      setResult(r);
      setTornado(t);
    } catch (err) {
      console.error("simulate failed", err);
      alert("Simulation failed; check the backend connection.");
    } finally {
      setRunning(false);
    }
  };

  const runDecision = async () => {
    setDecisionRunning(true);
    try {
      const [dr, dg, r, t] = await Promise.all([
        decision(inputs, di, iterations),
        decisionGrid(inputs, di, iterations),
        simulate(inputs, iterations),
        tornado(inputs, iterations),
      ]);
      setDecisionResult(dr);
      setDecisionGrid(dg);
      setResult(r);
      setTornado(t);
    } catch (err) {
      console.error("decision failed", err);
      alert("Decision analysis failed; check the backend connection.");
    } finally {
      setDecisionRunning(false);
    }
  };

  const isFactor = activeTab === "factor-analysis";
  const isRunning = isFactor ? running : decisionRunning;
  const runLabel = isFactor ? "Run Scenario" : "Run Decision Analysis";
  const onRun = isFactor ? runFactor : runDecision;

  const tabBtn = (isActive: boolean) =>
    "px-4 py-2 text-sm font-semibold border-x border-t border-ink rounded-t-md -mb-px " +
    (isActive
      ? "bg-canvas text-ink"
      : "bg-button-grey text-ink/60 hover:text-ink hover:brightness-95");

  return (
    <div className="min-h-screen flex flex-col bg-canvas">
      {/* Sticky header + tab nav freeze the page just below the tab line */}
      <div className="sticky top-0 z-30 bg-canvas print:hidden">
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
              onClick={onRun}
              disabled={isRunning}
              className="no-print px-3 py-1 bg-button-grey border border-ink rounded text-sm font-semibold text-ink hover:brightness-95 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isRunning ? "Running..." : runLabel}
            </button>
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

        <nav className="no-print border-b border-ink px-6 pt-3 bg-panel-grey/40 flex gap-1">
          <button
            className={tabBtn(activeTab === "factor-analysis")}
            onClick={() => setActiveTab("factor-analysis")}
          >
            Factor Analysis
          </button>
          <button
            className={tabBtn(activeTab === "decision-analysis")}
            onClick={() => setActiveTab("decision-analysis")}
          >
            Decision Analysis
          </button>
        </nav>
      </div>

      {/* On-screen tabbed UI — hidden in print */}
      <main className="flex-1 flex flex-col print:hidden">
        {activeTab === "factor-analysis" && (
          <>
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
                <ResultsView result={result} />
              ) : (
                <div className="rounded-xl border border-ink bg-canvas h-[300px] flex items-center justify-center text-ink text-sm">
                  Click Run Scenario to see the distribution and statistics
                </div>
              )}
            </section>
          </>
        )}

        {activeTab === "decision-analysis" && (
          <>
            <section className="border-b border-ink p-6 overflow-auto bg-canvas">
              <h2 className="text-base font-semibold text-ink mb-4 text-center">
                Decision Inputs
              </h2>
              <DecisionInputs />
            </section>

            <section className="p-6 bg-panel-grey/40">
              <h2 className="text-base font-semibold text-ink mb-4">
                Decision Results
              </h2>
              {decisionResult ? (
                <DecisionResults result={decisionResult} />
              ) : (
                <div className="rounded-xl border border-ink bg-canvas h-[300px] flex items-center justify-center text-ink text-sm">
                  Click Run Decision Analysis to see the net present value
                  distribution and drivers
                </div>
              )}
            </section>
          </>
        )}
      </main>

      {/* Print-only deliverable — always renders all four pages.
          Positioned off-screen on screen via .print-stage so Recharts
          can measure container dimensions correctly; @media print pulls
          it back into the document flow. */}
      <div className="print-stage" aria-hidden="true">
        <PrintPage1 />
        <PrintPage2 />
        <PrintPage3 />
        <PrintAppendix />
      </div>

      <footer className="border-t border-ink px-6 py-3 text-xs text-ink flex items-center justify-between gap-3 print:hidden">
        <span>Open FAIR Risk Calculator · React frontend</span>
      </footer>
      <References />
    </div>
  );
}
