# DW-TADS analyst frontend

React 18, strict TypeScript, Vite, Tailwind CSS v3, Framer Motion, Cytoscape.js (cose-bilkent), Recharts, Zustand, React Router v6, Axios and bundled Lucide icons.

## Setup and development

Use Node.js 20.19+ or 22.12+ and npm. From this directory:

```sh
npm ci
cp .env.example .env.local
npm run dev
```

Open http://localhost:5173. `VITE_DEMO_MODE=false` is the default. There are no seeded actors, fallback data, bundled credentials, or authentication bypasses. Login requires a real username, password and authenticator code. Inter and JetBrains Mono are served from `public/fonts/`; the browser makes no CDN or font-provider calls.

The development proxy forwards `/api/*` to `http://localhost:8010/*`, removing `/api` to match the required nginx behavior. `VITE_API_BASE_URL` defaults to `/api`. Set environment values before building; they are public build-time settings, not secrets.

## Build and deploy

```sh
npm test
npm run build
npm run preview
# From this directory, with analyst-api on the same Docker network:
docker build -t dw-tads-frontend .
docker run --rm -p 8080:80 --network dwtds-mvp dw-tads-frontend
```

`dist/` is the production artifact. Docker uses a Node 20 Alpine build and nginx Alpine runtime. nginx serves SPA routes and proxies `/api/` to `http://analyst-api:8010/`. Terminate HTTPS at the deployment ingress. Backend authorization remains authoritative; client role gating is only a navigation aid.

## Backend integration requirements

This frontend implements Section 9 of the supplied project brief. The existing `intel/app.py` in this repository implements a different public-technical-intelligence API: static bearer tokens, technical records instead of actor profiles, and different sources/graph/export routes. It is **not compatible** with this frontend's actor/JWT contract. A conforming analyst API on port 8010 is required. The frontend does not change or fabricate backend records.

Required endpoints: `POST /auth/token`, `GET /query/timeline`, `GET /query/actor/{id}`, `GET /query/graph`, `GET /query/sources`, `GET /query/audit`, `POST /export`, `GET /health`, `GET /ready`, `GET /metrics`.

JWTs are stored only in sessionStorage (`dwtds_token`); the expiry timestamp is stored alongside them. User and role are read from JWT claims (`username`/`sub`, `role`). The server must verify tokens and enforce all authorization. A 401 clears the session. Logout clears session credentials. Error toasts include correlation IDs when returned. GET network errors offer retry; 429 responses show Retry-After countdowns.

Contract limits are deliberately visible:

- User administration, case creation and actor comparison have no supplied endpoints. Their UI states explain that they are unavailable; no mutation is simulated.
- There is no demo TOTP generator endpoint or provisioned demo secret. Demo mode displays authenticator guidance, not a fabricated code.
- Exports use the server query ID. Local tier, maximum-confidence, search, selection, sort and column filters do not change the exported server query. The actor PDF action exports its originating timeline query, not an actor-specific report.
- Category is sent as a comma-separated list. Confirm this encoding with the deployed analyst API.
- Cache ratios describe the returned snapshot, because 24-hour source history is not in the contract. Activity deltas are not invented without prior-period data.
- Actor audit shows matching resources within the latest 100 entries; the API offers no actor-specific audit filter.
- Optional actor fields (Merkle root, wallet clusters, VASP deposits, correlations and related actors) are rendered when supplied. Missing fields are explicitly reported.
- System displays actual health/readiness and raw Prometheus metrics. Per-container URLs and standardized lag/cache/version metric names are not specified.

## Keyboard and accessibility

| Shortcut | Action |
| --- | --- |
| Ctrl/Cmd + K | Command palette |
| / | Search actors, handles, wallets and routes |
| F | Focus mode |
| Escape | Close modal / exit focus mode |
| Up / Down | Navigate result rows / palette entries |
| Enter | Open focused result |
| ? | Keyboard help and opt-in sound |

Tab controls support arrow keys, Home and End. Modals trap and restore focus. Graph nodes have a keyboard-accessible list below the canvas. Confidence and source states include text as well as color. Focus mode hides the sidebar and reduces motion; after 30 seconds idle, the top bar dims until interaction resumes. Relative timestamps share one timer. Reduced motion disables transforms, animated charts, graph layout animation, shimmers and spinners.

## Design system

`src/styles/tokens.css` is the source of truth for neutral surfaces, amber accent, semantic colors, typography, spacing, radius, shadows and motion. Tailwind exposes the color and font tokens. `/design-system` provides a compact swatch and component preview. Default body line-height is 1.7. The primary target is 1440×900; the sidebar collapses below 1280 and becomes a drawer below 1024. Viewports below 768 display the requested desktop-use message.

## Validation

See `VERIFICATION.md` for actual build, test and integration results. Automated API fixtures, if used for browser checks, are test-only and are not shipped in the app. Never treat fixture validation as verification of the production backend.