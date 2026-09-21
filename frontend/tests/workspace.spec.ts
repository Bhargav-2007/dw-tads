import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
const actor = {
  actor_id: "test-actor-001",
  risk_score: 0.86,
  category: ["hacking"],
  handles: ["test-handle"],
  wallets: [{ address: "test-wallet", currency: "BTC" }],
  confidence: 0.91,
  tier: "HIGH",
  last_seen: new Date().toISOString(),
  first_seen: "2026-01-01T00:00:00Z",
};
const source = {
  name: "Test collection",
  url: "https://example.org",
  last_fetch: new Date().toISOString(),
  record_count: 42,
  http_status: 200,
  cache_hit: true,
  success: true,
};
const token = (role = "admin") =>
  `eyJhbGciOiJub25lIn0.${Buffer.from(JSON.stringify({ sub: "test-analyst", role, exp: Math.floor(Date.now() / 1000) + 3600 })).toString("base64url")}.test`;
async function fixtures(page: Page, role = "admin") {
  await page.route("**/api/**", async (route) => {
    const u = new URL(route.request().url());
    let data: unknown;
    if (u.pathname === "/api/auth/token")
      data = {
        access_token: token(role),
        token_type: "bearer",
        expires_in: 3600,
      };
    else if (u.pathname === "/api/query/timeline")
      data = {
        results: [actor],
        query_id: "test-query",
        result_hash: "test-hash",
      };
    else if (u.pathname.startsWith("/api/query/actor/"))
      data = {
        actor,
        handles: [
          { handle_id: "test-handle", platform: "test", confidence: 0.9 },
        ],
        wallets: [{ address: "test-wallet", currency: "BTC", confidence: 0.9 }],
        pgp_keys: [],
        contacts: [],
        onion_services: [],
        clearnet_ips: [],
        stylometric_matches: [],
        behavioral_profile: {
          hourly_activity: Array.from({ length: 24 }, (_, i) => i % 5),
          timezone: "UTC",
        },
        attribution_confidence: {
          score: 0.91,
          contributions: { identifier: 0.7, behavior: 0.2 },
        },
        evidence_chain: [
          {
            sha256: "a".repeat(64),
            captured_at: new Date().toISOString(),
            source_url: "https://example.org/evidence",
            minio_key: "test/evidence",
          },
        ],
        result_hash: "test-hash",
      };
    else if (u.pathname === "/api/query/graph")
      data = {
        nodes: [
          {
            id: actor.actor_id,
            type: "Actor",
            label: actor.actor_id,
            risk_score: 0.86,
            tier: "HIGH",
          },
          {
            id: "test-handle",
            type: "Handle",
            label: "test-handle",
            tier: "HIGH",
          },
        ],
        edges: [
          {
            from: actor.actor_id,
            to: "test-handle",
            type: "USES",
            confidence: 0.9,
          },
        ],
        result_hash: "graph-test",
      };
    else if (u.pathname === "/api/query/sources")
      data = {
        sources: [source],
        total_records: 42,
        distinct_sources: 1,
        result_hash: "source-test",
      };
    else if (u.pathname === "/api/query/audit")
      data = {
        results: [
          {
            audit_id: "audit-test",
            ts: new Date().toISOString(),
            event_type: "query",
            actor_user: "test-analyst",
            action: "read",
            resource: actor.actor_id,
            query_hash: "q".repeat(64),
            result_hash: "r".repeat(64),
          },
        ],
        chain_valid: true,
        result_hash: "audit-test",
      };
    else if (u.pathname === "/api/export") {
      await route.fulfill({
        status: 200,
        contentType: "application/octet-stream",
        body: "test export",
        headers: { "X-Result-Hash": "export-test" },
      });
      return;
    } else if (u.pathname === "/api/metrics") {
      await route.fulfill({
        status: 200,
        contentType: "text/plain",
        body: "test_metric 1",
      });
      return;
    } else data = { status: "ok" };
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(data),
    });
  });
}
async function login(page: Page) {
  await page.goto("/login");
  await page.getByLabel("Username", { exact: true }).fill("test-analyst");
  await page.getByLabel("Password", { exact: true }).fill("test-password");
  await page.getByLabel("Authenticator code").fill("123456");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Investigation Timeline" }),
  ).toBeVisible();
}
test("login, investigation, exports and keyboard workflows", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await fixtures(page);
  await login(page);
  await expect(page.getByText(actor.actor_id, { exact: true })).toBeVisible();
  expect(
    await page.evaluate(() => sessionStorage.getItem("dwtds_token")),
  ).toBeTruthy();
  expect(
    await page.evaluate(() => localStorage.getItem("dwtds_token")),
  ).toBeNull();
  await page.keyboard.press("Control+k");
  await expect(page.getByRole("dialog")).toBeVisible();
  await page
    .getByRole("combobox", { name: "Search or jump to" })
    .fill("test-handle");
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/actor/);
  for (const tab of [
    "Identifiers",
    "Infrastructure",
    "Personas",
    "Blockchain",
    "Evidence",
    "Audit",
    "Overview",
  ]) {
    await page.getByRole("tab", { name: tab, exact: true }).click();
    await expect(page.getByRole("tabpanel", { name: tab })).toBeVisible();
  }
  await page.getByRole("link", { name: "Open full graph" }).click();
  await expect(
    page.getByRole("img", { name: /Relationship graph with 2 nodes/ }),
  ).toBeVisible();
  await page.getByLabel("Layout", { exact: true }).selectOption("circle");
  await page.getByRole("button", { name: "Fit graph" }).click();
  await page.getByText("Accessible node list").click();
  await page.getByRole("button", { name: `Actor · ${actor.actor_id}` }).click();
  await expect(
    page.getByRole("link", { name: "Open actor profile" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Data sources", exact: true }).click();
  await expect(
    page.getByText("Test collection", { exact: true }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Administration", exact: true }).click();
  await expect(
    page.getByText("Chain verified over 1 returned entries"),
  ).toBeVisible();
  await page.getByRole("button", { name: "audit-test", exact: true }).click();
  await expect(page.getByText("Query hash:", { exact: false })).toBeVisible();
  await page.getByRole("link", { name: "Timeline", exact: true }).click();
  await page.locator("summary").filter({ hasText: "Export" }).click();
  for (const format of ["CSV", "JSON", "PDF"]) {
    const download = page.waitForEvent("download");
    await page.getByRole("button", { name: format, exact: true }).click();
    expect((await download).suggestedFilename()).toBe(
      `dw-tads-test-query.${format.toLowerCase()}`,
    );
  }
  await page.locator("summary").filter({ hasText: "Export" }).click();
  await page.getByRole("heading", { name: "Investigation Timeline" }).click();
  await page.keyboard.press("f");
  await expect(page.locator(".app-shell")).toHaveClass(/focus-mode/);
  await page.keyboard.press("Escape");
  await expect(page.locator(".app-shell")).not.toHaveClass(/focus-mode/);
  await page.keyboard.press("?");
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  expect(errors).toEqual([]);
  for (const close of await page
    .getByRole("button", { name: "Dismiss notification" })
    .all())
    await close.click();
  await expect(
    page.getByRole("row", { name: `Open actor ${actor.actor_id}` }),
  ).toHaveCSS("opacity", "1");
  await page.screenshot({ path: "artifacts/timeline.png", fullPage: true });
});
test("role protection and unauthorized session clearing", async ({ page }) => {
  await fixtures(page, "analyst");
  await login(page);
  await page.goto("/admin");
  await expect(page).toHaveURL(/timeline/);
  await expect(
    page.getByRole("link", { name: "Administration", exact: true }),
  ).toHaveCount(0);
  await expect(page.getByText(actor.actor_id, { exact: true })).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Refresh", exact: true }),
  ).toBeEnabled();
  await page.route("**/api/query/timeline*", (route) =>
    route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ error: "Session expired" }),
    }),
  );
  await page.getByRole("button", { name: "Refresh", exact: true }).click();
  await expect(page).toHaveURL(/login/);
  expect(
    await page.evaluate(() => sessionStorage.getItem("dwtds_token")),
  ).toBeNull();
});
test("accessible pages, responsive layout and reduced motion", async ({
  page,
}) => {
  await fixtures(page);
  await page.goto("/login");
  await page.screenshot({ path: "artifacts/login.png" });
  let checks = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(checks.violations).toEqual([]);
  await login(page);
  for (const path of [
    "/timeline",
    "/sources",
    "/actor/test-actor-001",
    "/graph?actor_id=test-actor-001",
    "/admin",
  ]) {
    await page.goto(path);
    await page.waitForTimeout(800);
    checks = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();
    expect(checks.violations, `${path} accessibility`).toEqual([]);
    await page.screenshot({
      path: `artifacts/${path.split("?")[0].split("/")[1]}.png`,
      fullPage: true,
    });
  }
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto("/timeline");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.emulateMedia({ reducedMotion: "reduce" });
  expect(
    await page.evaluate(
      () => matchMedia("(prefers-reduced-motion: reduce)").matches,
    ),
  ).toBe(true);
  await page.setViewportSize({ width: 700, height: 900 });
  await expect(
    page.getByText(
      "DW-TADS is designed for desktop use. Please use a wider viewport.",
    ),
  ).toBeVisible();
});

test("virtualized timeline, server filters and recoverable API errors", async ({
  page,
}) => {
  await fixtures(page);
  const actors = Array.from({ length: 180 }, (_, i) => ({
    ...actor,
    actor_id: `actor-${String(i).padStart(3, "0")}`,
    risk_score: 1 - i / 200,
  }));
  await page.route("**/api/query/timeline*", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        results: actors,
        query_id: "many",
        result_hash: "many",
      }),
    }),
  );
  await login(page);
  await expect(page.getByText("actor-000", { exact: true })).toBeVisible();
  expect(await page.locator("tbody tr[tabindex]").count()).toBeLessThan(40);
  await page.locator(".results .table-scroll").evaluate((el) => {
    el.scrollTop = el.scrollHeight;
  });
  await expect(page.getByText("actor-179", { exact: true })).toBeVisible();
  const request = page.waitForRequest(
    (r) =>
      r.url().includes("/query/timeline") &&
      new URL(r.url()).searchParams.get("category") === "hacking",
  );
  await page.getByRole("button", { name: "hacking", exact: true }).click();
  await request;
  await expect(
    page.getByRole("button", { name: "Refresh", exact: true }),
  ).toBeEnabled();
  await page.route("**/api/query/timeline*", (route) =>
    route.fulfill({
      status: 429,
      headers: { "Retry-After": "2" },
      contentType: "application/json",
      body: JSON.stringify({
        error: "Rate limited",
        correlation_id: "test-correlation",
      }),
    }),
  );
  await page.getByRole("button", { name: "Refresh", exact: true }).click();
  await expect(
    page.getByText("Too many requests", { exact: true }),
  ).toBeVisible();
  await expect(page.getByText(/Try again in/)).toBeVisible();
  await page.getByText("Request details", { exact: true }).click();
  await expect(
    page.getByText("test-correlation", { exact: true }),
  ).toBeVisible();
});
