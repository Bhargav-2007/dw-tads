import type { Tier } from "../types/api";
export const tiers: Tier[] = ["HIGH", "MEDIUM", "LOW", "INSUFFICIENT"];
export const tierColor = (tier: Tier) => `var(--status-${tier.toLowerCase()})`;
export const getTier = (v: number): Tier =>
  v >= 0.8 ? "HIGH" : v >= 0.5 ? "MEDIUM" : v > 0 ? "LOW" : "INSUFFICIENT";
