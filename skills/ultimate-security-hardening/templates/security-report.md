# Security Report — {{project}}

- Commit audited: `{{commit}}` · generated {{generated_at}} · depth: {{asvs_level}}
- Standards: OWASP Top 10 2025 · ASVS 5.0.0 · API-Top10 2023 · WSTG 4.2 · CWE Top 25 · CVSS/EPSS/KEV (snapshot {{snapshot_date}})
- Tools run: {{tools_with_versions}} · lanes skipped: {{skipped_with_reason}}

## 1. Executive summary
{{three_lines_max: state, biggest risk, release recommendation}}

## 2. Scope
in-scope: {{dirs/stacks}} · out-of-scope: {{exclusions + why}}

## 3. Findings
| ID | Sev | Category | Location | Status | Fix | Evidence (masked) |
|---|---|---|---|---|---|---|
{{one row per finding — full detail in security-findings.json}}

## 4. Fixes applied
{{diff summaries · class (SAFE/REVIEW/HIGH-RISK) · verification link}}

## 5. Regression tests
{{authored/reused · pass/fail · before/after proof}}

## 6. Re-scan results
{{detector reruns · newly clean · newly introduced (→ back to audit)}}

## 7. Residual risks
{{open items + next action + owner}}

## 8. Coverage ledger
ran: {{lanes}} · gaps: {{gaps — these force INCOMPLETE if critical}}

## Release verdict: {{PASS | PASS WITH WARNINGS | BLOCKED | INCOMPLETE}}
{{one-line justification tied to verdict rules (never PASS with critical gaps)}}
