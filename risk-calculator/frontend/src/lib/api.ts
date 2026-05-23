import { InputKey, SimResult, Triangular } from "./state";

const pert = (t: Triangular) => ({ type: "pert", min: t.min, likely: t.likely, max: t.max });

export async function simulate(
  inputs: Record<InputKey, Triangular>,
  iterations: number,
  seed = 42
): Promise<SimResult> {
  const payload = {
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
  const r = await fetch("/api/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
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
