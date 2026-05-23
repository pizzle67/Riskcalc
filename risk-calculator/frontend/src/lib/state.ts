import { create } from "zustand";

export type Triangular = { min: number; likely: number; max: number };

export type InputKey =
  | "contactFrequency"
  | "probabilityOfAction"
  | "threatCapability"
  | "resistanceStrength"
  | "primaryLoss"
  | "secondaryLossFrequency"
  | "secondaryLossMagnitude";

export const INPUT_META: Record<
  InputKey,
  { label: string; unit: string; bound: [number, number]; step: number }
> = {
  contactFrequency:       { label: "Contact Frequency",         unit: "per year",     bound: [0, 365],    step: 1 },
  probabilityOfAction:    { label: "Probability of Action",     unit: "probability",  bound: [0, 1],      step: 0.01 },
  threatCapability:       { label: "Threat Capability",         unit: "0 to 1",       bound: [0, 1],      step: 0.01 },
  resistanceStrength:     { label: "Resistance Strength",       unit: "0 to 1",       bound: [0, 1],      step: 0.01 },
  primaryLoss:            { label: "Primary Loss",              unit: "USD",          bound: [0, 1e9],    step: 1000 },
  secondaryLossFrequency: { label: "Secondary Loss Frequency",  unit: "probability",  bound: [0, 1],      step: 0.01 },
  secondaryLossMagnitude: { label: "Secondary Loss Magnitude",  unit: "USD",          bound: [0, 1e9],    step: 1000 },
};

const DEFAULTS: Record<InputKey, Triangular> = {
  contactFrequency:       { min: 4,        likely: 12,       max: 36 },
  probabilityOfAction:    { min: 0.05,     likely: 0.20,     max: 0.50 },
  threatCapability:       { min: 0.40,     likely: 0.60,     max: 0.80 },
  resistanceStrength:     { min: 0.30,     likely: 0.50,     max: 0.70 },
  primaryLoss:            { min: 50_000,   likely: 250_000,  max: 1_000_000 },
  secondaryLossFrequency: { min: 0.10,     likely: 0.30,     max: 0.60 },
  secondaryLossMagnitude: { min: 25_000,   likely: 150_000,  max: 750_000 },
};

type Materiality = {
  metric: "manual" | "market_cap" | "revenue" | "net_income";
  value: number;
  threshold: number;
};

export type ScenarioMetaKey =
  | "scenarioNumber"
  | "asset"
  | "threatCommunity"
  | "threatType"
  | "effect";

export type ScenarioMeta = Record<ScenarioMetaKey, string>;

export type SimResult = {
  summary: {
    mean: number;
    median: number;
    p10: number;
    p25: number;
    p75: number;
    p90: number;
    p95: number;
    var_95: number;
    cvar_95: number;
    min: number;
    max: number;
    std: number;
  };
  histogram: { counts: number[]; bins: number[] };
  exceedance: { values: number[]; probabilities: number[] };
  iterations: number;
  tornado?: { input: string; rho: number }[];
};

type Store = {
  inputs: Record<InputKey, Triangular>;
  baselines: Record<InputKey, Triangular>;
  rationales: Record<InputKey, string>;
  sector: string;
  iterations: number;
  materiality: Materiality;
  csfTiers: Record<string, number>;
  csfTiersEnabled: boolean;
  scenarioMeta: ScenarioMeta;
  tableFrozen: boolean;
  treeHidden: boolean;
  referencesOpen: boolean;
  result: SimResult | null;
  running: boolean;
  setLeaf: (key: InputKey, value: Triangular) => void;
  setLikelyProportional: (key: InputKey, newLikely: number) => void;
  setSector: (s: string, defaults: Record<InputKey, Triangular>) => void;
  resetToBaseline: (key: InputKey) => void;
  setRationale: (key: InputKey, value: string) => void;
  setMateriality: (m: Partial<Materiality>) => void;
  setCsfTier: (fn: string, tier: number) => void;
  setCsfTiersEnabled: (b: boolean) => void;
  setIterations: (n: number) => void;
  setScenarioMeta: (key: ScenarioMetaKey, value: string) => void;
  setTableFrozen: (b: boolean) => void;
  setTreeHidden: (b: boolean) => void;
  setReferencesOpen: (b: boolean) => void;
  setResult: (r: SimResult | null) => void;
  setRunning: (b: boolean) => void;
};

const EMPTY_RATIONALES: Record<InputKey, string> = {
  contactFrequency: "",
  probabilityOfAction: "",
  threatCapability: "",
  resistanceStrength: "",
  primaryLoss: "",
  secondaryLossFrequency: "",
  secondaryLossMagnitude: "",
};

export const useStore = create<Store>((set) => ({
  inputs: { ...DEFAULTS },
  baselines: { ...DEFAULTS },
  rationales: { ...EMPTY_RATIONALES },
  sector: "custom",
  iterations: 10000,
  materiality: { metric: "manual", value: 1_000_000, threshold: 1.0 },
  csfTiers: { identify: 2, protect: 2, detect: 2, respond: 2, recover: 2 },
  csfTiersEnabled: false,
  scenarioMeta: { scenarioNumber: "", asset: "", threatCommunity: "", threatType: "", effect: "" },
  tableFrozen: false,
  treeHidden: false,
  referencesOpen: false,
  result: null,
  running: false,
  setLeaf: (key, value) =>
    set((s) => ({ inputs: { ...s.inputs, [key]: value } })),
  setLikelyProportional: (key, newLikely) =>
    set((s) => {
      const current = s.inputs[key];
      if (current.likely > 0 && Number.isFinite(newLikely)) {
        const ratio = newLikely / current.likely;
        const next = {
          min: current.min * ratio,
          likely: newLikely,
          max: current.max * ratio,
        };
        return { inputs: { ...s.inputs, [key]: next } };
      }
      return { inputs: { ...s.inputs, [key]: { ...current, likely: newLikely } } };
    }),
  setSector: (sector, defaults) =>
    set(() => ({ sector, baselines: defaults, inputs: { ...defaults } })),
  resetToBaseline: (key) =>
    set((s) => ({ inputs: { ...s.inputs, [key]: s.baselines[key] } })),
  setRationale: (key, value) =>
    set((s) => ({ rationales: { ...s.rationales, [key]: value } })),
  setMateriality: (m) =>
    set((s) => ({ materiality: { ...s.materiality, ...m } })),
  setCsfTier: (fn, tier) =>
    set((s) => ({ csfTiers: { ...s.csfTiers, [fn]: tier } })),
  setCsfTiersEnabled: (b) => set(() => ({ csfTiersEnabled: b })),
  setIterations: (n) => set(() => ({ iterations: n })),
  setScenarioMeta: (key, value) =>
    set((s) => ({ scenarioMeta: { ...s.scenarioMeta, [key]: value } })),
  setTableFrozen: (b) => set(() => ({ tableFrozen: b })),
  setTreeHidden: (b) => set(() => ({ treeHidden: b })),
  setReferencesOpen: (b) => set(() => ({ referencesOpen: b })),
  setResult: (r) => set(() => ({ result: r })),
  setRunning: (b) => set(() => ({ running: b })),
}));
