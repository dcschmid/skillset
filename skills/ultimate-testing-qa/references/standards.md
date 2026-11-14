# Standards & version provenance

Probe discipline: these numbers are a snapshot. At task time, the project's
own lockfile/`node_modules` is authoritative; re-probe npm `latest` only when
creating fresh configs or upgrading.

## Pinned baseline (npm `latest` dist-tag, probed 2026-11-14)

| Package | Version | Role | Compatibility note |
|---|---|---|---|
| playwright / @playwright/test | 1.65.1 | E2E, browser automation | `expect` ships from `@playwright/test`, NOT from `playwright` (that package is the library; exports `devices`, not `expect`) |
| vitest | 5.1.0 | unit/integration | peer `vite ^6.4.0 \|\| ^7.0.0 \|\| ^8.0.0` — follow the PROJECT's vite major |
| @vitest/coverage-v8 | 5.1.0 | coverage | exact-match vitest minor |
| axe-core / @axe-core/playwright | 4.14.0 | inline a11y checks | same engine as the `accessibility` skill's tool |
| msw | 3.0.5 | network-level mocking | works in Vitest (node env) and Playwright-adjacent setups |
| @testing-library/dom | 10.4.2 | user-centric queries | base for framework wrappers |
| @testing-library/react | 16.3.3 | React components | React 19 OK |
| @testing-library/vue | 8.1.0 | Vue SFC components | needs @vitejs/plugin-vue in Vitest config |
| @testing-library/svelte | 5.4.2 | Svelte 5 components | svelte 5.x |
| @testing-library/user-event | 14.6.10 | interaction simulation | pairs with jsdom env |
| lighthouse / @lhci/cli | 13.6.0 / 0.16.1 | perf/a11y lab audits | optional lane, defer deep CWV to `seo-performance` skill |
| jsdom / happy-dom | 31.0.1 / 21.0.4 | DOM env | happy-dom faster; jsdom broader |

Framework context (for detection, not install): astro 7.4.12, next 16.4.6,
nuxt 4.6.4, svelte 5.57.3, vite 8.3.8.

## Rules

1. `npm view <pkg> version` at task start for anything you install; record
   the date next to the number in generated configs.
2. Vitest major MUST match the project's Vite major (peer range above).
   Never drop Vitest 5 onto a Vite 5 project — install Vitest 1/2/3 per the
   old peer ranges instead.
3. Playwright: `@playwright/test` for test runner + assertions; `playwright`
   only as a library. Browsers installed once: `npx playwright install
   --with-deps` (needs network; report NOT TESTED per-browser when offline).
4. axe-core version parity with the `accessibility` skill (4.14) keeps
   findings comparable across skills.
5. Re-pin cadence: quarterly or on major release of Playwright/Vitest;
   human review before editing this table.

## Sources (checked 2026-11-14)

- https://playwright.dev/docs/release-notes · https://vitest.dev/config/
- https://mswjs.io/docs · https://testing-library.com/docs/
- https://developer.chrome.com/docs/lighthouse · https://github.com/axe-core
