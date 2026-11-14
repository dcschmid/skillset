# Visual Regression — before/after comparison discipline

Purpose: VISUAL_REGRESSION_REVIEW mode and Phase 5/6 of fix workflows. Proves
changes did not break surfaces — and that intended changes landed. A pixel diff
alone is NEVER a design verdict.

## Conditions parity (both sides, or don't compare)

same viewport set · same browser+version · comparable data state (seeded/demo
data, logged-in as same role) · same theme (light AND dark separately) ·
animations frozen (`prefers-reduced-motion` emulate or CSS injection) · fonts
loaded (wait networkidle/fonts ready) · scroll to top, fixed header/dynamic
timestamps noted. Capture via `scripts/screenshot_audit.sh` (reuses the
project's or the accessibility skill's Playwright); name files
`<route>-<viewport>-<theme>.png` so pairs are mechanical.

## Classify every difference

| Class | Meaning | Action |
|---|---|---|
| intended | matches an approved fix | keep; cite the fix id |
| regression | unintended visual break (overflow, overlap, clipped text, lost state) | fix now, P1+ |
| dynamic | data/timestamp/content legitimately differs | annotate, not a defect |
| technical | AA/font-loading/scrollbar artifacts | tune capture conditions, re-shoot once |

## Verdicts

`PASS` (no regressions, intended diffs verified) · `FAIL` (regressions listed
with route+viewport+pair paths) · `NOT AVAILABLE` (no browser; never a fake
PASS). Report embeds pair paths + per-diff class; scores stay with
`visual-quality-gates.md`, diffs only show change.

## Baseline policy

Before AUDIT_AND_FIX / DESIGN_MODERNIZATION: capture baseline of affected
routes if browser exists; store outside source tree or in project's existing
screenshot dir per repo policy. No baseline → review is source-diff based and
says so.
