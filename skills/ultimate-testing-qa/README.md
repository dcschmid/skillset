# ultimate-testing-qa

Universal Testing & QA skill for coding agents: test architecture for new
web projects, additive test extension for existing ones, browser/runtime
audits, E2E (Playwright, 3 engines), unit/integration (Vitest), defect
fix-retest loops, QA reports, CI lanes. Framework-agnostic (Astro, React,
Next, Vue/Nuxt, Svelte, Vite, vanilla, static HTML).

- Entry: `SKILL.md` (mode gate A–F + shared analyzer step)
- Depth: `references/` (standards pins, analysis matrix, architecture,
  playwright-e2e, vitest-unit, fix-retest, reporting, ci-integration)
- Tool: `scripts/qa.mjs analyze|report` (Node stdlib, zero deps, offline)
- Templates: `assets/` (report md skeleton, GitHub Actions QA lane)
- Validate: `node tests/run.mjs` → `VERDICT PASS/FAIL`

Baselines pinned 2026-11-14 (Playwright 1.65.1, Vitest 5.1.0, axe 4.14.0) —
re-probed against each project's lockfile at task time.
