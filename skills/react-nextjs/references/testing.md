# Testing — strategy & release gate

## Pyramid per project type

| Layer | Tool (project default or opt-in) | Scope |
|---|---|---|
| Static | `tsc --noEmit`, ESLint (+ `eslint-plugin-react-hooks`) | every change |
| Unit | Vitest (or project runner) | pure logic, reducers, validators, DTO mappers |
| Component | React Testing Library + vitest | user-visible behavior, a11y (axe) on components |
| Integration | RTL + mocked network, or MSW | feature flows w/ boundary types |
| E2E | Playwright (Firefox default) | critical user flows, routes, forms, auth |
| Visual/perf | Playwright screenshots / Lighthouse CI | when budget exists |

**Async Server Components are not unit-test friendly** — test them through
integration/E2E (rendered route), not by importing into Vitest. Say so in
reports instead of shipping brittle RSC unit tests.

## Rules

- Test behavior (rendered text, roles, transitions), not implementation
  (hook call counts, snapshots of markup structure).
- Every bugfix: failing regression test first when a test can hold it; RSC
  path → E2E assertion instead.
- Queries/data: fixed fixtures; no live network in unit/component tests;
  no wall-clock sleeps — `findBy`/`waitFor` semantics.
- a11y: axe on key routes (jest-axe/vitest + axe-core); keyboard walk manual.
- Playwright: locators by role/label; run headless; `webServer` boot the app;
  flaky test = bug (fix or quarantine with issue).
- New project: wire the runner stack before feature depth (one smoke test per
  layer beats 40 unit tests on utils).

## Release gate (10-point, all green or NOT production-ready)

1. `npx tsc --noEmit`
2. `npm run lint` (incl. hooks rules)
3. unit+component tests green (`vitest run`)
4. `npm run build` clean (warnings triaged)
5. E2E critical flows green (Playwright)
6. a11y: axe clean on key routes + keyboard walk of primary flows
7. no known critical security findings (audit + review of perimeter fns per
   security.md)
8. no unexplained hydration errors in console/build
9. API/DB calls observed healthy (no 5xx in E2E traces/logs)
10. perf budgets vs baseline (bundle sizes + lab CWV where scope demands)

Report failures as failures with the command output excerpt; never claim a
gate passed that didn't run.
