# Audit Methodology

The pipeline is binding: **Understand → Baseline → Detect → Prioritize →
Refactor → Verify → Compare → Report**. Never skip Baseline before Detect,
never skip Verify before the next Refactor step.

## Phase contract

| Phase | Output | Gate to next phase |
|---|---|---|
| 1 Discovery | project fingerprint (`scripts/detect_project.py`), tool inventory | languages + check commands known or explicitly `unknown` |
| 2 Baseline | test/lint/typecheck results as-is | pre-existing failures listed file by file |
| 3 Analysis | findings with `file:line` evidence | every finding cites evidence or says "not measurable" |
| 4 Plan | risk class + test strategy per work package | user approval for HIGH-risk packages |
| 5 Refactor | one controlled change | diff = intended change only |
| 6 Verify | `verify_changes.py` verdict | PASS or explained UNVERIFIED |
| 7 Recover | targeted revert of own hunks | foreign edits untouched |
| 8 Continue | next package | package independence holds |
| 9 Final | full relevant suite + gates | green vs baseline |
| 10 Report | delta + residual risk | measured values only |

## Evidence rules

1. A finding without a `file:line` pointer is not reported.
2. A metric without a measurement base is `N/A`, never an estimate.
3. "Green tests" ≠ "behavior preserved": state residual risk regardless.
4. Absent tooling is a documented gap, not a silent skip — list it under
   "missing capabilities" in every report.
5. Auditor bias: audit mode never edits application code. Fixes happen only
   in explicitly entered fix modes (SAFE AUTOFIX, DEEP REFACTOR, DEBT CLEANUP).

## Quick vs deep

- **QUICK AUDIT** (changed files + direct callers): `run_audit.py --quick` on
  the diff scope; baseline = branch-point diff vs merge base; verification =
  affected tests only. Use pre-merge.
- **DEEP AUDIT** (full tree or module): full bundle, then per-finding risk
  classification. Default read-only.

## Unknown language / unknown project

When `detect_project.py` reports `primary_language: unknown` or a language
with no adapter (`references/language-adapters.md`): stay generic
(line counts, duplication windows, TODO markers), refuse automated edits,
and mark every deeper check UNVERIFIED. A cautious generic audit beats a
confident wrong one.
