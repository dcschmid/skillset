# Test architecture (framework-agnostic)

## Pyramid, sized per project type

```
        E2E (Playwright)            few: critical journeys only
   Integration (Vitest + msw +      real components, mocked network
   Testing Library / framework)
 Unit (Vitest, node env, no DOM)    pure logic, reducers, utils, validators
```

Node-env unit tests are the cheap majority; anything below integration must
run in milliseconds. E2E count: journeys × happy+error path, not pages.

## Per-framework wiring (config snippets, adapt to project's Vite major)

### Vitest (all JS/TS stacks)
- Zero-config inside `vite.config.*` via `test` key when a Vite project
  exists; separate `vitest.config.*` otherwise.
- environment: `node` default; `jsdom`/`happy-dom` for component tests.
- Astro: test `.astro` via `@astrojs/compiler`/`getCollection` at integration
  level; UI logic in `.astro` is tested through exported helpers + Playwright.
- Vue: `@vitejs/plugin-vue` + `@vue/test-utils` or TL/vue in jsdom.
- Svelte 5: `@testing-library/svelte` + `svelte` vite plugin; run:browser
  mode only when CSS/animation matters.
- React/Next: TL/react; App-Router server components = integration/unit
  tests of the data functions + Playwright for the rendered page.
- Coverage: `@vitest/coverage-v8` matching vitest minor; thresholds only as
  high as current reality, ratchet upward.

### Playwright
- `playwright.config.ts` with `projects: chromium, firefox, webkit`
  (WebKit needs install; offline → report NOT TESTED for it).
- `webServer` entry reuses the project's own dev/preview command — never a
  parallel server with different env.
- Reuse the existing config when present; extend `testDir` list if needed.

## Greenfield minimal set (only when analyzer says no runner exists)

1. `vitest` (vite-major-matched) + `vitest.config` + `npm run test`.
2. `@playwright/test` + config + `npm run test:e2e` + first journey spec.
3. `.github/workflows/qa.yml` from `assets/github-actions-qa.yml`.
4. README lines with the two commands + how to add a test.

## Conventions the project already has win

Test placement (colocation vs `tests/`), naming (`*.test.ts` vs `*.spec.ts`
vs `test_*.py`), fixtures location, mock style (manual vs msw vs vi.mock) —
copy the dominant existing style even if a different one is fashionable.

## Anti-patterns (report as defects in review, never ship)

- E2E-heavy pyramids (100 Playwright tests, 0 unit).
- Tests asserting implementation (private state, call counts) instead of
  user-visible behavior.
- Global setup that boots the whole app for a pure function.
- Snapshot everything (snapshot sprawl = broken-window test suite).
  Snapshot: small components + CLI output; handwritten asserts: logic.
- `skip`/`fixme` without issue link; retry-as-flakiness-cure (max 1 retry,
  triage the trace, never default retries up).
