import { beforeEach, describe, expect, it, vi } from "vitest";
const { get } = vi.hoisted(() => ({ get: vi.fn() }));
vi.mock("../lib/api", () => ({
  api: { get },
  errorMessage: (e: Error) => e.message,
}));
import { useTimelineStore, defaultFilters } from "./timelineStore";
const actor = {
  actor_id: "test-1",
  risk_score: 0.8,
  confidence: 0.9,
  tier: "HIGH",
  category: [],
  handles: [],
  wallets: [],
  last_seen: "",
};
beforeEach(() => {
  get.mockReset();
  useTimelineStore.setState({
    filters: { ...defaultFilters },
    results: [],
    queryId: null,
    loading: false,
    error: null,
  });
});
describe("query consistency", () => {
  it("rejects incompatible technical-record responses", async () => {
    get.mockResolvedValue({
      data: { results: [{ id: "CVE-test" }], query_id: "q" },
    });
    await useTimelineStore.getState().fetch();
    expect(useTimelineStore.getState().error).toContain("does not match");
    expect(useTimelineStore.getState().queryId).toBeNull();
  });
  it("only invalidates export IDs when server filters change", () => {
    useTimelineStore.setState({ queryId: "q" });
    useTimelineStore.getState().setFilters({ tier: "HIGH" });
    expect(useTimelineStore.getState().queryId).toBe("q");
    useTimelineStore.getState().setFilters({ category: ["hacking"] });
    expect(useTimelineStore.getState().queryId).toBeNull();
  });
  it("does not let a stale request replace newer evidence", async () => {
    let resolveOld: (v: unknown) => void = () => {};
    get.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          resolveOld = resolve;
        }),
    );
    const old = useTimelineStore.getState().fetch();
    get.mockResolvedValueOnce({
      data: { results: [actor], query_id: "new", result_hash: "new" },
    });
    await useTimelineStore.getState().fetch();
    resolveOld({ data: { results: [], query_id: "old", result_hash: "old" } });
    await old;
    expect(useTimelineStore.getState().queryId).toBe("new");
    expect(useTimelineStore.getState().results).toHaveLength(1);
  });
  it("clears stale exports on server failure", async () => {
    useTimelineStore.setState({ queryId: "old" });
    get.mockRejectedValue(new Error("Offline"));
    await useTimelineStore.getState().fetch();
    expect(useTimelineStore.getState().queryId).toBeNull();
    expect(useTimelineStore.getState().loading).toBe(false);
    expect(useTimelineStore.getState().error).toBe("Offline");
  });
});
