# QA Report — {{project}}

Generated {{date}} · stack {{frameworks+versions}} · tools
{{playwright/vitest/axe versions}} · scope: {{routes/tiers covered}}
Unavailable: {{what could not run and why}}

## Results

| Check | Status | Detail | Evidence | Fix |
|---|---|---|---|---|
| {{tier-1 journey}} | PASS/FAIL/NEEDS REVIEW/NOT TESTED | {{what ran}} | {{path/command}} | {{commit/file or —}} |

## Fix-retest log

| Defect | Root cause | Fix | Before→After | Regression lock |
|---|---|---|---|---|
| {{symptom}} | {{file/invariant}} | {{diff summary}} | FAIL→PASS | {{test file}} |

## Manual review queue (never empty silently)

- [ ] {{visual diff / a11y incomplete / copy decision}} — reviewer, due

## Coverage map

{{coverage % + files <50%}} · uncovered risk: {{tier assignment}}

## Next actions

{{owner: action}} — report cadence: {{PR lane / nightly}} refs
reporting.md contract. Automated evidence and manual review are separate;
NOT TESTED is never PASS.
