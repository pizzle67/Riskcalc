import {
  DecisionGridResult,
  DecisionInputs,
  DecisionResult,
  InputKey,
  SimResult,
  Triangular,
} from "./state";

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

function decisionPayload(
  inputs: Record<InputKey, Triangular>,
  control: DecisionInputs
) {
  return {
    baseline: {
      contact_frequency:         pert(inputs.contactFrequency),
      probability_of_action:     pert(inputs.probabilityOfAction),
      threat_capability:         pert(inputs.threatCapability),
      resistance_strength:       pert(inputs.resistanceStrength),
      primary_loss:              pert(inputs.primaryLoss),
      secondary_loss_frequency:  pert(inputs.secondaryLossFrequency),
      secondary_loss_magnitude:  pert(inputs.secondaryLossMagnitude),
    },
    control: {
      loss_reduction:            pert(control.lossReduction),
      implementation_cost:       pert(control.implementationCost),
      ongoing_cost:              pert(control.ongoingCost),
      discount_rate:             pert(control.discountRate),
      cancellation_probability:  control.cancellationProbability,
      horizon_years:             control.horizonYears,
      ramp_up_year:              control.rampUpYear,
      efficacy_decay:            control.efficacyDecay,
      salvage_value:             control.salvageValue,
      residual_loss_floor:       control.residualLossFloor,
    },
  };
}

export async function decision(
  inputs: Record<InputKey, Triangular>,
  control: DecisionInputs,
  iterations: number,
  seed = 42
): Promise<DecisionResult> {
  const { baseline, control: controlPayload } = decisionPayload(inputs, control);
  const r = await fetch("/api/decision", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ iterations, seed, baseline, control: controlPayload }),
  });
  if (!r.ok) throw new Error(`decision failed: ${r.status}`);
  const data = await r.json();
  return {
    summary: data.summary,
    probPositive: data.prob_positive,
    probCancelled: data.prob_cancelled,
    expectedBaselineAle: data.expected_baseline_ale,
    expectedAnnualSavings: data.expected_annual_savings,
    histogram: data.histogram,
    exceedance: data.exceedance,
    tornado: data.tornado,
    horizonYears: data.horizon_years,
    rampUpYear: data.ramp_up_year,
    iterations: data.iterations,
  };
}

export async function decisionGrid(
  inputs: Record<InputKey, Triangular>,
  control: DecisionInputs,
  iterations: number,
  gridSize = 12,
  seed = 42
): Promise<DecisionGridResult> {
  const { baseline, control: controlPayload } = decisionPayload(inputs, control);
  const r = await fetch("/api/decision-grid", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      iterations,
      seed,
      grid_size: gridSize,
      baseline,
      control: controlPayload,
    }),
  });
  if (!r.ok) throw new Error(`decision-grid failed: ${r.status}`);
  const data = await r.json();
  const scenario = (s: any) => ({
    baselineAle: s.baseline_ale,
    ongoingCost: s.ongoing_cost,
    discountRate: s.discount_rate,
    grid: s.grid,
  });
  return {
    costAxis: data.cost_axis,
    reductionAxis: data.reduction_axis,
    pessimistic: scenario(data.pessimistic),
    likely: scenario(data.likely),
    optimistic: scenario(data.optimistic),
    marker: data.marker,
    horizonYears: data.horizon_years,
    iterations: data.iterations,
  };
}
