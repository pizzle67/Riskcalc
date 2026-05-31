import { Triangular } from "./state";

export const mean = (t: Triangular) => (t.min + t.likely + t.max) / 3;

export function vulnerabilityFromGrid(tcap: Triangular, rs: Triangular): number {
  const grid = 21;
  const tcapVals: number[] = [];
  const rsVals: number[] = [];
  for (let i = 0; i < grid; i++) {
    const p = i / (grid - 1);
    tcapVals.push(triPpf(p, tcap));
    rsVals.push(triPpf(p, rs));
  }
  let negative = 0;
  let total = 0;
  for (let i = 0; i < grid; i++) {
    for (let j = 0; j < grid; j++) {
      if (i === j) continue;
      total++;
      if (rsVals[j] - tcapVals[i] < 0) negative++;
    }
  }
  return total === 0 ? 0 : negative / total;
}

function triPpf(p: number, t: Triangular): number {
  if (p <= 0) return t.min;
  if (p >= 1) return t.max;
  const c = (t.likely - t.min) / Math.max(t.max - t.min, 1e-12);
  return p < c
    ? t.min + Math.sqrt(p * (t.max - t.min) * (t.likely - t.min))
    : t.max - Math.sqrt((1 - p) * (t.max - t.min) * (t.max - t.likely));
}

export function rollupTef(cf: Triangular, poa: Triangular): number {
  return cf.likely * poa.likely;
}

export function rollupLef(tef: number, vuln: number): number {
  return tef * vuln;
}

export function rollupSecondaryLoss(slef: Triangular, slm: Triangular): number {
  return slef.likely * slm.likely;
}

export function rollupLm(pl: Triangular, sl: number): number {
  return pl.likely + sl;
}

export function rollupRisk(lef: number, lm: number): number {
  return lef * lm;
}

export function fmtUsd(v: number): string {
  return `$${Math.round(v).toLocaleString("en-US")}`;
}

export function fmtUsdShort(v: number): string {
  const abs = Math.abs(v);
  const sign = v < 0 ? "-" : "";
  if (abs >= 1_000_000_000) return `${sign}$${(abs / 1_000_000_000).toFixed(1)}B`;
  if (abs >= 1_000_000) return `${sign}$${(abs / 1_000_000).toFixed(1)}M`;
  if (abs >= 1_000) return `${sign}$${(abs / 1_000).toFixed(0)}K`;
  return `${sign}$${Math.round(abs)}`;
}

export function fmtPct(v: number): string {
  return `${Math.round(v * 100)}%`;
}

export function fmtCount(v: number): string {
  return `${Math.round(v)}`;
}
