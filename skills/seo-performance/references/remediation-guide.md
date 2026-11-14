# Remediation — classes, gates, verification

Fix taxonomy (autoFixClass) and their approval status:

| class | scope | auto? | typical fix |
|---|---|---|---|
| robots-txt | robots.txt directives | yes | Sitemap line, narrow Disallow |
| sitemap-cleanup | sitemap entries | yes | drop noindex/dead, regen via framework |
| static-html-meta | built HTML meta | yes | inject viewport/charset canonical |
| static-html-lang | built HTML lang | yes | add lang attr |
| (img alt) | built HTML img | yes | alt="" decorative / descriptive |
| canonical-changes | canonical strategy | **approval** | per-page canonicals in template |
| redirects | server/route config | **approval** | collapse chains, fix loops |
| content-removal | content | **approval** | — |
| architecture / framework-migration | stack | **approval** | e.g. CSR→SSR |

## Repair loop (binding)
1. baseline snapshot (never fix without `latest.json`).
2. smallest root-cause change, project-native idiom, existing design system.
3. writes land as git diff + `.seo-report/fixes-dry|applied.patch`.
4. verify: build → existing tests → browser spot check → re-audit →
   `compare`. Done = finding gone in new snapshot AND no regressions.
5. residual problems + risks documented, not buried.

## Severity ladder for triage
critical: broken routes/loops/server errors · high: blocked indexation,
JS-only content, missing titles on important pages, budget error breaches ·
medium: wrong canonicals, dead sitemap entries, hreflang gaps, blocking
scripts, slow TTFB · low: polish (descriptions, lang, alt).

## Design & a11y protection (never traded)
Layout/nav/interaction/contrast preserved; a11y findings have their own
severity path (delegate to accessibility skill if present); budgets are
edited to measured reality, ideals never block merges silently.

## Regression protection
safe site: budgets + weekly monitor + pre-release `--profile strict`.
fix applied: re-run same command, compare snapshots, keep both JSONs.
