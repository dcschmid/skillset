# Audit Methodology & Auto-Fix

Engine: `audit_harness.py`. Findings schema:
`schemas/audit-report.schema.json`. The 0..100 score is transparent weighted;
categories without observable material are **skipped** (excluded from the
denominator) — never scored 0, never credited.

## Finding record (every finding, no exceptions)

id • category • severity • component (file/line/quote = evidence — no
evidence, no finding) • technical cause • impact • concrete improvement •
fixability (yes/review/no; "review" = manual steps documented) • risk of the
fix itself.

## Category → evidence source

architecture/reliability/recovery/security: agent code (loops bounded? breaks?
silent excepts? secrets? shell bounds?) · tools: JSON manifests · context:
instruction files (size, duplication, injection surface) · observability:
recorded traces · test-coverage: test files · performance/multi-agent: require
runtime metrics / delegation config — offline absent ⇒ skipped+reasoned.

## Auto-fix workflow (ordered, reversible)

1. inspect state (git status; foreign changes respected, never touched)
2. audit → findings
3. prioritize by severity × fixability
4. show plan (dry-run default; writes nothing)
5. approvals for HIGH/CRITICAL fix-risks
6. apply only deterministic, small, testable edits — currently: JSON tool
   manifest de-duplication. Code fixes stay proposals: editing arbitrary code
   without running its tests would violate "repairs are test-backed".
7. run the project's tests
8. regression check (compare_benchmarks / re-audit)
9. regression found → revert (git), document why
10. repair report (findings fixed / deferred + manual steps)

Rules: dry-run never writes; no mass edits; no deletion of unknown files; no
gate bypass; existing behavior preserved; failed tests ⇒ halt + revert path.
