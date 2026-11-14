# Project analysis: detection matrix

Run `node scripts/qa.mjs analyze [dir]` first; this matrix covers what the
script cannot see and how to act on each result. Analysis is READ-ONLY:
never create configs, install deps, or touch test files during analysis.

## What to determine, in order

| Fact | Evidence | If missing |
|---|---|---|
| Framework + version | package.json deps + config files (astro.config.*, next.config.*, nuxt.config.*, svelte.config.js, vite.config.*) | vanilla/HTML → browser tests via static server or `npx serve` |
| Package manager | lockfile > `packageManager` field | infer from README/CI; NEVER install with the wrong pm (lockfile churn = side effect) |
| Build/dev commands | `scripts` in package.json; framework defaults | ask CI config; a wrong dev command wastes every E2E run |
| Rendering mode | framework config `output`/adapter (Astro), `next build` mode, nuxt ssr flag | read the built `dist/`/`out/`: HTML present = SSG/SSR, empty shell = CSR |
| Routes | `src/pages`, `app/`, `src/routes`, `pages/`, astro `src/pages` | static site: crawl from entry with `link[rel=canonical]`/nav links |
| Existing tests | analyzer `testFiles` + runner configs | greenfield only then; otherwise EXTEND |
| Auth | login routes, middleware/proxy/auth dirs, session cookies | document auth-required routes as scenario-blocked, report NOT TESTED |
| API surface | route handlers (`app/api`, `src/server`, server.js), fetch targets, openapi.json | mock via msw in tests; live API tests need base URL from .env(.example) |
| Breakpoints | CSS media queries / tailwind.config / theme | default mobile+desktop viewports (375×667, 1280×800) |

## Act on existing assets (binding)

1. Runner exists → same runner, same config; add files in existing locations
   and naming (`*.test.ts` next to source vs `tests/` — copy the project).
2. E2E exists (playwright/cypress) → extend specs; do NOT port to the other.
3. Coverage configured → respect thresholds; raise incrementally, never
   lower silently.
4. Two runners coexist (vitest+jest, playwright+cypress) → the dominant one
   wins for NEW tests; note the split in the report, resolve only on request.

## Risk ranking (drives depth, not page count)

Tier 1 (always deep): auth, payment/checkout, form submit+validation,
data mutations, API contracts, anything the user named as critical journey.
Tier 2: navigation, search, list pages, SSR-rendered content (hydration).
Tier 3: static content, docs, legal pages — smoke only (loads, no console
errors, no failed requests). Depth per tier: T1 unit+integration+E2E+visual,
T2 integration+E2E smoke, T3 smoke. State tiering in the delivered strategy.

## Output shape

Analyzer JSON + a short strategy: stack truth → test pyramid for THIS stack →
tiered targets → files to create → commands to run → what stays NOT TESTED
and why. No installs until the user sees the plan, unless the task was
explicitly "set it up".
