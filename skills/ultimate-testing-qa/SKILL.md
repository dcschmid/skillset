---
name: ultimate-testing-qa
description: >
  Universal testing and QA engineering for ANY web project and framework (Astro, React,
  Next.js, Vue/Nuxt, Svelte/SvelteKit, Vite, vanilla JS/TS, static HTML; baselines
  Playwright, Vitest, axe-core re-probed against the project lockfile at task time). Use for
  ANY testing/QA task on ANY web surface: equip projects with a test architecture, extend
  existing suites, audit live sites for runtime/console/network errors, run E2E and
  cross-browser flows, build unit/integration/component tests, detect visual and responsive
  regressions, test forms, check APIs, reproduce bugs, FIX root causes in editable source,
  re-test after fixes, generate QA reports, wire CI/CD gates. Ships a zero-dep Node analyzer
  (scripts/qa.mjs: analyze|report) detecting framework, package manager, runners, routes, CI
  - evidence-only reports. When source is editable: reproduce -> locate -> fix -> retest ->
  regression. Existing setups extended, never replaced without cause. Automated PASS !=
  quality claim: untested paths report NOT TESTED.
---

# Ultimate Testing & QA (universal)

Baselines (probe live; never trust these over the project's lockfile):
**Playwright 1.65.1** · **Vitest 5.1.0** · **axe-core 4.14.0** ·
**MSW 3.0.5** · **Lighthouse 13.6.0 / @lhci/cli 0.16.1** · Node 22 LTS ·
probed 2026-11-14 (`references/standards.md`).

## Prime Directive

Extend, never replace. Analyze what exists before adding anything. Fix the
root cause in source, not the symptom in a test. Every report line maps to
evidence: a run, a screenshot, a trace, a diff. Missing coverage is NOT
TESTED, never PASS. No framework migrations to impose a personal standard.

## Mode gate (pick the spine first)

| Mode | Trigger | Spine |
|---|---|---|
| **A Architect** | new project, "set up testing" | analyze → risk-ranked strategy → test pyramid → gates |
| **B Extend** | existing project, "add tests" | inventory existing tests → gap map → minimal additive tests |
| **C Audit** | "check this site for errors" | routes → console/network/runtime → visual/responsive → report |
| **D E2E/Journey** | user flows, forms, auth, cross-browser | journey scripts → Playwright → traces → triage |
| **E Fix-retest** | bug found, "fix and verify" | reproduce → isolate → root cause → minimal fix → retest → regression test |
| **F CI** | "wire QA into CI/CD" | existing pipeline → additive job → exit-code gate |

Then run the shared entry: analyze first, always.

## Entry (every mode)

```bash
node scripts/qa.mjs analyze [project-dir]        # detection JSON, stdlib-only
node scripts/qa.mjs analyze [project-dir] --format md
```

Reads lockfiles, package.json, configs, routes, CI, existing tests.
Reports `detected` / `unavailable` separately. Load
`references/project-analysis.md` for the detection matrix; load the matching
`references/test-architecture.md` section only after the analyzer ran.

## Workflow A/B — architecture & extension

1. Analyzer result decides stack truth: framework, runner, package manager,
   SSR/SSG/CSR, monorepo, existing runners.
2. Reuse existing runners/configs; add a runner only if none exists AND the
   project type demands one (`references/test-architecture.md`).
3. Risk-rank targets: critical journeys, forms/auth/payments, API contracts,
   rendered routes → depth per risk, not per page.
4. Pyramid: pure unit (no DOM) < integration (msw + real components) <
   E2E (few, journeys) < visual snapshots (golden, gated).
5. Deliver configs + tests + one runnable command; verify it executes.

## Workflow C/D — live audit & E2E

`references/playwright-e2e.md` (patterns below are binding):
1. Enumerate routes (analyzer output), start dev/preview server yourself.
2. Per route: console errors, failed requests, uncaught exceptions
   (`page.on('console'|'pageerror')`, `response` status) — these are DEFECTS.
3. Interact: forms submit + validation messages, nav, auth flows, responsive
   (mobile+desktop viewports), cross-browser chromium/firefox/webkit.
4. Visual: `toHaveScreenshot()` baselines only where diffs are meaningful.
5. Failure → Workflow E. `--trace on-first-retry` for repro.
A11y on a live site: defer to the `accessibility` skill's audit tool when the
host has it; run axe inline (`@axe-core/playwright`) otherwise; report both
the same: automated PASS != conformance.

## Workflow E — fix-retest loop (the core, not optional)

Full protocol `references/fix-retest.md`:
reproduce (failing test is the artifact) → minimize → locate source (LSP/
grep on stack frames) → smallest fix preserving intent → re-run failing test
→ run affected suite → add regression test if none exists → update report
before/after. Never mark fixed on inspection alone.

## Workflow F — CI

Additive GitHub Actions lane, correct exit codes, artifact upload of
report+traces: `assets/github-actions-qa.yml`, `references/ci-integration.md`
(Docker, caching, flake policy, `--only-changed` on PRs, full on main).

## Reporting (every delivery)

`node scripts/qa.mjs report results.json --format md,html` from
`references/reporting.md` contract + `assets/qa-report.md`. Statuses:
PASS / FAIL / NEEDS REVIEW / NOT TESTED. Automated and manual evidence are
NEVER merged into one number.

## Binding rules

1. Existing configs/runners are authoritative; changes need a stated reason.
2. Every claim cites evidence; no invented scores, no PASS without a run.
3. Fixes are minimal, in source, root-caused; test-only fixes that hide
   source bugs are banned (except flaky-test quarantine, documented).
4. Vitest major follows the project's Vite major (`node_modules/vitest`
   peerDependencies), never a global latest onto an old project.
5. One skill never rewrites another's domain: a11y depth = `accessibility`
   skill, SEO/CV = `seo-performance` skill; this skill owns test
   architecture, E2E, unit/integration, fix-retest, QA reporting.
6. Outputs non-destructive: reports get dated suffixes on collision.
7. Never fake SR/browser presence: environment can't run WebKit → report
   NOT TESTED with reason.

## References (load per need)

`references/standards.md` pins+provenance+dates ·
`project-analysis.md` detection matrix ·
`test-architecture.md` pyramid+risk model ·
`playwright-e2e.md` browser E2E/responsive/forms/auth/network ·
`vitest-unit.md` unit/integration/mocking/coverage ·
`fix-retest.md` diagnose→fix→retest protocol ·
`reporting.md` report contract · `ci-integration.md` GitHub Actions/Docker.
Tools: `scripts/qa.mjs` (analyze|report, Node stdlib) ·
assets: report templates + CI workflow. Validate: `node tests/run.mjs`
→ `VERDICT PASS/FAIL`.
