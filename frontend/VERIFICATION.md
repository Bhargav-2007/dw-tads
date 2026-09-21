# Verification — 21 September 2026

## Delivered and running

- Source: `frontend/`, with all requested route, store, hook, design-token and component modules.
- Development preview: http://localhost:5173/login, running from the actual workspace using native WSL Node 20.19.0. HTTP 200 confirmed after final changes.
- Production output: `frontend/dist/`, rebuilt from the final source.
- Pinned package versions and lockfile, local Inter/JetBrains Mono fonts and licenses, Dockerfile, nginx configuration, environment example and setup documentation included.

## Results

| Check | Result |
| --- | --- |
| Strict TypeScript + Vite production build | Passed in native WSL |
| Unit tests | 9 passed |
| Playwright browser suites | 4 passed in Chrome against native WSL Vite |
| Axe WCAG 2 A/AA + 2.1 AA checks | No violations on login, timeline, actor, graph, sources and admin tested views |
| Lighthouse login accessibility | 100 / 100 |
| Complete compressed build including local fonts | Approximately 485 KB gzip; below 800 KB target |
| Desktop horizontal overflow at 1280 px | Passed |
| Narrow-screen desktop-use message | Passed |
| Reduced-motion preference | Passed |

Browser verification covered sessionStorage login, absence of localStorage JWT storage, role-gated navigation, 401 session clearing, all seven actor tabs, command search, focus mode and Escape, graph layout/fit/node selection, source display, expanded audit rows, all three export download formats, 180-row virtualization, server category parameters, and Retry-After/correlation-ID handling. Download tests verify the client request and browser download behavior with fixture blobs, not the validity of a real backend PDF.

Screenshots in `artifacts/` contain explicitly synthetic test fixtures from `tests/workspace.spec.ts`. Fixtures are intercepted by the test runner and are not bundled into the application. Screenshot animations are settled for reproducible visual inspection. Small-graph automatic zoom was capped after visual review to prevent oversized nodes and labels.

The larger graph chunk emits Vite's uncompressed 500 KB advisory. It is split from the main bundle; the aggregate compressed artifact remains below the requested limit.

## Integration limitations

The required analyst service on localhost:8010 was unavailable. The existing repository's `intel/app.py` implements a different token, record, graph and export API from the brief. Real end-to-end login, actor queries, source/audit data and generated exports therefore remain unverified and require a conforming backend. The frontend rejects incompatible timeline records rather than displaying invented actor data.

The supplied contract has no user-management, case, comparison or demo-TOTP generation endpoints. Those actions are unavailable or explicitly explained in the UI. Export is scoped to the originating server query, not selected rows or an individual actor. Optional enrichment and metrics only appear when the backend supplies them. README documents each contract assumption and missing endpoint.

Docker runtime integration, a sustained eight-hour session, an overall layout-shift score, and every fine-grained animation timing were not independently certified. Graph animation uses native Cytoscape layout transitions and hover dimming; it does not implement SVG stroke-dashoffset edge drawing.

## Dependency review

The final audit records zero high and zero critical findings. Four moderate reports remain: React Router/react-router-dom under the mandatory v6 constraint, and the development-only Vitest/mocker pair. `README.md` records the usage constraints and mitigations; `artifacts/final-audit.json` contains the exact findings. This frontend should not be represented as fully production-certified until the backend integration and residual dependency review are complete.

## Repeat verification

```sh
npm ci
npm test
npm run build
npm run dev
# In another terminal with Chrome installed:
npm run test:e2e
```

Use Node 22.19+ for the full optional Lighthouse toolchain. See README for the project-local native WSL runtime already used in this workspace.