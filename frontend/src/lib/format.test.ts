import { describe, it, expect } from "vitest";
import { relativeTime, safeUrl, shortHash } from "./format";
import { getTier } from "./tier";
describe("evidence display safety", () => {
  it("does not permit executable evidence URLs", () => {
    expect(safeUrl("javascript:alert(1)")).toBeUndefined();
    expect(safeUrl("data:text/html,test")).toBeUndefined();
    expect(safeUrl("https://example.org/evidence")).toBe(
      "https://example.org/evidence",
    );
  });
  it("preserves both ends of identifiers", () =>
    expect(shortHash("abcdefghijklmnopqrstuvwx", 4)).toBe("abcd…uvwx"));
  it("handles missing timestamps without inventing recency", () =>
    expect(relativeTime("")).toBe("Not reported"));
  it("calculates relative evidence age", () =>
    expect(
      relativeTime("2026-09-21T10:00:00Z", Date.parse("2026-09-21T12:00:00Z")),
    ).toBe("2 hours ago"));
  it("uses explicit confidence boundaries", () => {
    expect(getTier(0.8)).toBe("HIGH");
    expect(getTier(0.5)).toBe("MEDIUM");
    expect(getTier(0.1)).toBe("LOW");
    expect(getTier(0)).toBe("INSUFFICIENT");
  });
});
