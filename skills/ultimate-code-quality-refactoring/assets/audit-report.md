# Quality Audit — {{PROJECT}}

_Generated {{TIMESTAMP}} · mode: {{MODE}} · read-only unless fix mode active_

## 1. Executive Summary
- Languages: {{LANGUAGES_WITH_COUNTS}}
- Frameworks: {{FRAMEWORKS_OR_NONE}}
- Monorepo: {{MONOREPO_FLAG}} ({{PACKAGES_OR_NA}})
- Files measured: {{N}} (skipped {{N}}) | Hotspots: {{N}} | Clone groups: {{N}}
- Verification: {{PASS_COUNT}}/{{TOTAL}} checks pass vs baseline | UNVERIFIED: {{LIST}}

## 2. Findings (every finding cites evidence)
| # | Priority | Class | Location | Evidence | Impact | Risk | Effort | Action |
|---|---|---|---|---|---|---|---|---|
| F1 | P0-P3 | smell/arch/dup/complexity/dead-code | file:line | measured output / diff | | LOW/MED/HIGH | S/M/L | |

## 3. Architecture
Dependency/boundary findings or "no structural findings". Cycles: {{CYCLES}}.

## 4. Duplicate candidates
Merge only where sites change together. Intentional duplicates: listed as wontfix.

## 5. Complexity hotspots (measured proxies)
| File | Lines | Nesting | CC-proxy | Long>50 | Debt |

## 6. Verification & baseline
Executed checks: {{CMDS}}. Pre-existing failures (baseline, not caused by change):
{{TEST_IDS}}. Flaky: {{LIST_OR_NONE}}.

## 7. Recommendations (prioritized, independent packages)
1. {{PACKAGE}} — benefit / risk / verification.

## 8. Roadmap
Ordered packages; each ends green vs baseline before the next starts.

---
Metrics from collectors are proxies (labeled); unavailable = N/A; no score
without a published formula.
