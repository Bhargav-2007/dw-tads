import { create } from "zustand";
import { api, errorMessage } from "../lib/api";
import type { GraphNode, GraphEdge, GraphResponse } from "../types/api";
let request = 0;
export const useGraphStore = create<{
  actorId: string;
  depth: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
  filters: { nodeTypes: string[]; tier: string };
  loading: boolean;
  error: string | null;
  configure: (s: {
    actorId?: string;
    depth?: number;
    filters?: { nodeTypes: string[]; tier: string };
  }) => void;
  fetch: () => Promise<void>;
}>((set, get) => ({
  actorId: "",
  depth: 1,
  nodes: [],
  edges: [],
  filters: { nodeTypes: [], tier: "All" },
  loading: false,
  error: null,
  configure: (s) => set(s),
  fetch: async () => {
    if (!get().actorId.trim()) return;
    const id = ++request;
    set({ loading: true, error: null });
    try {
      const { data } = await api.get<GraphResponse>("/query/graph", {
        params: { actor_id: get().actorId, depth: get().depth },
      });
      if (!Array.isArray(data.nodes) || !Array.isArray(data.edges))
        throw new Error("Unexpected graph response");
      if (id === request) set({ ...data, loading: false });
    } catch (e) {
      if (id === request)
        set({ loading: false, error: errorMessage(e), nodes: [], edges: [] });
    }
  },
}));
