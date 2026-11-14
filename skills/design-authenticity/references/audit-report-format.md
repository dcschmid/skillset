# Audit Report Format

Every full audit (AUDIT, AUDIT_AND_FIX, DESIGN_MODERNIZATION close) emits
`reports/design-authenticity-audit.md` (project default; honor an existing
reports dir/naming convention instead). Git-ignore generated reports only if
the project already ignores generated artifacts. Concrete, specific, checkable;
screenshot refs on visual findings.

```markdown
# Design Authenticity Audit — <project> — <date>
## 1 Project overview      framework · styling · tokens · routes(n) · runnability
## 2 Audit scope           full | route | component | viewport | theme — from request
## 3 Tools used            what actually ran (browser? a11y tool? build?) + fallbacks
## 4 Surfaces+states checked  list; NOT TESTED list with reasons
## 5 Findings summary      counts by severity; one line each
## 6 Design authenticity score  rubric axes before/after (existing-project modes)
## 7 Problems by severity  blocker/major/minor/nit + finding schema (anti-ai-patterns.md)
## 8 Recommendations       inside-system-first; risky ones as proposals, not applied
## 9 Fixes planned/applied file → change → finding-id
## 10 Before/after         score table + screenshot pairs (only from real captures)
## 11 Test results         commands + exit codes actually observed
## 12 Open problems        incl. iteration-cap leftovers
## 13 Audit limitations    missing browser/tools, sampling, source-only axes
```

Rules: score numbers only from observed evidence — no renders → visual axes =
`VISUAL_REVIEW_REQUIRED`, total marked partial. A review-requested audit stops
at § 8/9 (planned); applying fixes belongs to AUDIT_AND_FIX only.
