---
name: seo-performance
description: >
  Universal SEO and web-performance expert for new and existing websites, any framework
  (Astro, Next.js app/pages, React/Vite/CSR, static, CMS via URL). Use for auditing
  technical SEO (crawling, indexability, canonicals, sitemaps, robots, hreflang), Core Web
  Vitals (LCP/INP/CLS/TTFB/TBT, lab-vs-field discipline), delivered-HTML vs JS-rendered DOM
  checks, schema.org/JSON-LD validation, content/metadata quality, AI-search readiness,
  remediation with approval-gated safe auto-fixes, before/after verification, CI quality
  gates, regression monitoring. Use when asked to audit/fix/optimize a site's SEO or speed,
  'why is LCP bad', check indexation/schema/hreflang, prepare a release, or wire SEO into CI
  - not for pure feature work. Ships a zero-dependency Node auditor (scripts/seo.mjs:
  audit|fix|performance|technical|content|schema|monitor|ci|compare|serve) plus optional
  Lighthouse/Unlighthouse/LHCI/Playwright; works offline, no API keys; never invents scores.
---

# SEO & Web Performance (universal)

Working modes: **audit** (evidence), **fix** (safe edits, approval-gated),
**verify** (before/after snapshots). Frameworks auto-detected; versions
probed at task time, never assumed. Baselines verified 2026-11-14
(see `references/audit-methodology.md`).

## Prime directives
1. Delivered bytes are truth: check what crawlers receive *before* JS runs;
   a CSR app "passes" nothing its HTML never contained.
2. Lab ≠ field: Lighthouse scores are lab data; INP is field-only (CrUX/RUM).
   Missing data is reported UNAVAILABLE — never estimated, never zeroed.
3. Fixes target root causes in the project's own stack; no dependency
   sprawl, no framework migrations without approval, no content removal,
   no design/a11y regressions to buy milliseconds.
4. Optimization never means deleting substance. Scores never promise rankings.
5. Every fix cycle: baseline snapshot → fix → build+tests+re-audit → compare.

## Entry: pick the workflow, load ONE reference

| Task | Command (run from skill dir or absolute path) | Deep-dive |
|---|---|---|
| "audit this site/project" | `node scripts/seo.mjs audit <dir\|url>` | `references/audit-methodology.md` |
| quick pre-commit check | `... audit <t> --level 1` | same, §Level 1 |
| full site/CI gate | `... audit <t> --profile strict` | `references/technical-seo.md` |
| fix what you found | `node scripts/seo.mjs fix <t>` (dry-run) → `--apply` | `references/remediation-guide.md` |
| slow pages / CWV | `node scripts/seo.mjs performance <t>` | `references/core-web-vitals.md`, `references/performance-optimization.md` |
| indexation/robots/canonical | `... technical <t>` | `references/technical-seo.md` |
| metadata/content quality | `... content <t>` | `references/content-seo.md` |
| JSON-LD/schema | `node scripts/seo.mjs schema <t>` | `references/structured-data.md` |
| AI search/AEO/GEO | audit + read | `references/ai-search.md` |
| recurring/CI | `... ci <t> [--init]`, `... monitor <t>` | `references/audit-methodology.md` §CI |
| before/after | `node scripts/seo.mjs compare <a.json> <b.json>` | `templates/remediation-plan.md` |

Framework context (load when detected by `detectProject` output):
Astro → `references/astro.md` · Next.js → `references/nextjs.md` ·
React/Vite → `references/react.md`. Google rule base:
`references/google-search-guidelines.md`.

## Audit levels (auto-escalate, never silently)
- **L1 quick**: entry page metadata, status, canonical, robots, sitemap,
  render-gap smoke, first perf sample. Minutes.
- **L2 full** (default): sampled page types, mobile+desktop, CWV, links,
  schema, content, indexability, framework checks.
- **L3 deep**: sitewide crawl (only when `--max-pages` raised), render
  diffing, waterfalls, i18n reciprocity, duplicate study, repair plan.
Sampling by page type first is the rule on large sites; full crawl is
opt-in.

## Workflow (fix mode, binding)
1. **Discover** — `detectProject`: framework, rendering, SEO surface,
   existing tooling. Respect existing implementations; extend, don't replace.
2. **Baseline** — audit → snapshot saved under `.seo-report/`. This is the
   "before"; no fix starts without it.
3. **Triage** — findings carry severity/impact/cause-confidence/effort/risk/
   autoFixClass. Safe classes (static meta/lang, robots.txt, sitemap cleanup,
   img-alt) auto-apply only with `--apply`. Canonical rewrites, redirects,
   content removal, architecture/framework changes: **propose, await approval**.
4. **Fix** — smallest root-cause change in project-native idiom. Git-tracked
   diffs; fix patches land in `.seo-report/fixes-*.patch`.
5. **Verify** — build, tests, re-audit, `compare` snapshots. A fix is done
   when the finding disappears from the snapshot AND nothing regressed.
   Report residual problems honestly.

## Tool policy
Stdlib auditor first (works offline, no keys). Optional local tools probed
via `scripts/seo.mjs tools` / project deps: lighthouse 13.x, @lhci/cli 0.16.x,
unlighthouse 0.19.x, playwright 1.6x. Prefer project deps → `npx --no-install`.
No system installs, no paid APIs required, ever; PSI/CrUX/GSC enhance only
when the user provides access. External URLs: read-only, robots-respecting,
rate-limited, same-host, no forms/logins/writes.

## Output contract
Reports: exec summary → findings table (ID/severity/URL/evidence/cause/fix/
effort/risk/verify) → perf table (measured only) → data gaps as UNAVAILABLE
lists. Management summary = plain language, no score worship. JSON snapshots
in `.seo-report/` feed trend + CI. Never publish invented numbers.

## Cross-skill cooperation (optional, never required)
Works standalone. If sibling skills exist, delegate their domains:
`astro`/`react-nextjs` for framework internals, `accessibility` for a11y
depth (never sacrifice it for speed), `human-writing` for content rewrites
(brand voice preserved, diff-first, no fabricated claims).
