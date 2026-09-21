import { create } from "zustand";
import { api, errorMessage } from "../lib/api";
import type { Actor, TimelineResponse, Tier } from "../types/api";
export interface Filters {
  start: string;
  end: string;
  category: string[];
  minConfidence: number;
  maxConfidence: number;
  tier: Tier | "All";
}
export const defaultFilters: Filters = {
  start: "",
  end: "",
  category: [],
  minConfidence: 0,
  maxConfidence: 1,
  tier: "All",
};
let request = 0;
export const useTimelineStore = create<{
  filters: Filters;
  results: Actor[];
  queryId: string | null;
  loading: boolean;
  error: string | null;
  resultHash: string;
  setFilters: (f: Partial<Filters>) => void;
  fetch: () => Promise<void>;
}>((set, get) => ({
  filters: { ...defaultFilters },
  results: [],
  queryId: null,
  loading: false,
  error: null,
  resultHash: "",
  setFilters: (f) =>
    set((s) => ({
      filters: { ...s.filters, ...f },
      queryId:
        "start" in f || "end" in f || "category" in f || "minConfidence" in f
          ? null
          : s.queryId,
    })),
  fetch: async () => {
    const id = ++request;
    set({ loading: true, error: null, queryId: null });
    const f = get().filters;
    try {
      const { data } = await api.get<TimelineResponse>("/query/timeline", {
        params: {
          start: f.start || undefined,
          end: f.end || undefined,
          min_confidence: f.minConfidence,
          category: f.category.length ? f.category.join(",") : undefined,
        },
      });
      if (
        !Array.isArray(data.results) ||
        data.results.some(
          (a) =>
            typeof a.actor_id !== "string" ||
            typeof a.risk_score !== "number" ||
            typeof a.confidence !== "number" ||
            !["HIGH", "MEDIUM", "LOW", "INSUFFICIENT"].includes(a.tier),
        )
      )
        throw new Error(
          "The API response does not match the actor timeline contract",
        );
      if (id === request)
        set({
          results: data.results,
          queryId: data.query_id || null,
          resultHash: data.result_hash,
          loading: false,
        });
    } catch (e) {
      if (id === request)
        set({ loading: false, error: errorMessage(e), results: [] });
    }
  },
}));
