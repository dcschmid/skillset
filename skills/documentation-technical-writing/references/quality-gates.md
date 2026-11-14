# Quality gates, CI, docs sites

Gate vocabulary everywhere: PASS / WARN / FAIL / REVIEW_REQUIRED / NOT RUN.
Release is blocked while P0/P1 open; unrun checks stay NOT RUN in the report.

## Layered checks (this skill ships the first layer)

| Layer | Tool | Verdicts | When |
|---|---|---|---|
| structure+links | scripts/docs_check.py | PASS/FAIL offline | every docs PR |
| coverage audit | scripts/docs_audit.py | WARN/FAIL vs project | on demand, releases |
| drift | scripts/docs_sync.py | REVIEW_REQUIRED plan | after code merges |
| prose | vale / human-writing lint | WARN | if project wants style rules |
| markdown rules | markdownlint-cli2 | WARN | if installed |
| external links | lychee (timeouts, rate limit, error class) | WARN/FAIL | scheduled job, not every PR |
| API specs | redocly / project's validator | FAIL on invalid | when specs exist |
| diagrams | mmdc / project renderer | NOT RUN when absent | docs build |

## CI wiring (extend, never replace existing configs)

Markdown + local links on docs paths first (cheap, offline); style lint
behind a continue-on-error until tuned; external links and builds in a
separate job. Add the step to the project's REAL CI system (GitHub Actions,
GitLab CI…) — docs-only change still runs the docs lane. Report artifact =
JSON from scripts (--json --out) so verdicts are diffable.

## Docs sites

No platform unless the content needs one: plain Markdown in-repo beats a
framework. When a site is requested: pick the project's stack (Starlight for
Astro projects, MkDocs for Python-first, Docusaurus/VitePress/Sphinx where
already present) — never install a second framework next to the existing
docs. Site features (search, versioning, i18n, a11y, SEO) route to the
owning skills (accessibility, seo-performance, i18n); this skill keeps nav,
IA and content true.

## Scoring (report only, never replaces checks)

100-pt rubric: correctness 30 (verified claims, runnable commands),
completeness 20 (project-relevant questions answered), clarity 20
(single-mode docs, direct prose), currency 15 (synced to current code),
maintainability 10 (structure, diffability), security 5 (no secrets).
≥90 release target; any P0 security or proven-wrong install step blocks
regardless of total. Missing evidence = NOT RUN areas, score reported with
them listed.
