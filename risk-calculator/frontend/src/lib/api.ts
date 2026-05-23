import { InputKey, SimResult, Triangular } from "./state";

const pert = (t: Triangular) => ({ type: "pert", min: t.min, likely: t.likely, max: t.max });

function buildPayload(
  inputs: Record<InputKey, Triangular>,
  iterations: number,
  seed: number
) {
  return {
    name: "Risk Scenario",
    iterations,
    seed,
    contact_frequency: pert(inputs.contactFrequency),
    probability_of_action: pert(inputs.probabilityOfAction),
    threat_capability: pert(inputs.threatCapability),
    resistance_strength: pert(inputs.resistanceStrength),
    primary_loss: pert(inputs.primaryLoss),
    secondary_loss_frequency: pert(inputs.secondaryLossFrequency),
    secondary_loss_magnitude: pert(inputs.secondaryLossMagnitude),
  };
}

export async function simulate(
  inputs: Record<InputKey, Triangular>,
  iterations: number,
  seed = 42
): Promise<SimResult> {
  const r = await fetch("/api/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(buildPayload(inputs, iterations, seed)),
  });
  if (!r.ok) throw new Error(`simulate failed: ${r.status}`);
  const data = await r.json();
  return {
    summary: data.summary,
    histogram: data.histogram,
    exceedance: data.exceedance,
    iterations: data.iterations,
  };
}

export type TornadoRow = { input: string; rho: number };

export async function tornado(
  inputs: Record<InputKey, Triangular>,
  iterations: number,
  seed = 42
): Promise<TornadoRow[]> {
  const r = await fetch("/api/tornado", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(buildPayload(inputs, iterations, seed)),
  });
  if (!r.ok) throw new Error(`tornado failed: ${r.status}`);
  const data = await r.json();
  return data.rows as TornadoRow[];
}
