# Audit methodology — levels, sampling, CI, monitoring

## Levels
**L1 quick** (`--level 1`): entry page only — status, title/description/
canonical/viewport, robots+sitemap presence, first perf sample, obvious a11y.
Use pre-commit and after every small fix.
**L2 full** (default): sample by page type (home, listing, content, legal)
→ technical + CWV budgets + links + schema + content + framework checks,
mobile+desktop noted.
**L3 deep** (`--profile strict` or `--level 3`, raise `--max-pages`):
full crawl, render parity, i18n reciprocity, duplicate/orphan study,
repair plan. Large sites: sampling first is mandatory; full crawl explicit.

## Sampling rule
Identify page types from routes/sitemap → pick 1-3 exemplars per type →
audit exemplars → generalize template-level findings (canonical/desc/
headings are template bugs once, not N findings). Report says "pattern on
template X, affects ~N pages".

## Evidence & honesty contract
Every finding: id, severity, url/file, reproducible evidence (bytes/status),
probable cause, fix, effort, risk, verification command. Missing inputs are
UNAVAILABLE, gaps listed in report's dataGaps. Never a number without a
measurement; never lab-labelled-field.

## Monitoring
`seo.mjs monitor <dir>` writes weekly GH Action (cron Mon 06:00) + keeps
snapshots in `.seo-report/` (keep 12). `compare <before> <after>` classifies:
noise (≤ tolerancePct, default 10%) · regression · improvement ·
environmentChanged (framework/Node differs → compare invalidated).
No background daemons without explicit config.

## CI (`seo.mjs ci <dir>`, exit-code gate)
checks: SEO-critical errors, dead routes, metadata, indexability, schema
syntax, budgets (lab metrics only; INP excluded from gate), findings
report uploaded as artifact. `--init` writes lighthouserc.cjs + workflow.
Gate policy: fail on critical/high non-noise; warn below; retries=2 and
tolerance handle lab noise; project budgets in `config/performance-budgets.json`.
Local parity: same command, no keys, stdlib — CI and laptop run identically.

## Version baseline (probe at task time, `seo.mjs tools`)
node ≥18.17 · lighthouse 13.6.0 · @lhci/cli 0.16.1 · unlighthouse 0.19.1 ·
playwright 1.65.1 · astro 7.4.x · next 16.x (verified 2026-11-14; re-probe
before citing).
