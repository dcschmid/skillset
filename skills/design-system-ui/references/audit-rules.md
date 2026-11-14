# Audit rules + safe-fix ladder (AUDIT / FIX workflows)

## Evidence model (ds.mjs audit output)

`{severity P0..P3, kind confirmed|heuristic, rule, detail, evidence file:line,
impact}`. **confirmed** = textual fact (N occurrences, dup declaration,
missing var target) → auto-fixable when the fix is mechanical.
**heuristic** = threshold/shape signal (contrast-review, button-variants,
dark-fragmented) → needs project decision first. Never "fix" a heuristic
blindly. Report skeleton: assets/audit-report.md — summary · findings by P ·
locations · impact · fix · effort · auto-fixable vs design-decision split.
Unscanned scope (minified/generated/node_modules/large-file cap) = NOT
TESTED section, never "clean".

## Rule set (what each means + the safe fix)

| rule | sev | fix ladder |
|---|---|---|
| focus-hidden (`outline:none` w/o replacement) | P0 | add focus-visible replacement (token `focus-indicator`) per file, verify keyboard walk |
| missing-ref / circular-ref (tokens) | P0 | repair alias target; if target deleted → repoint to semantic equivalent, run tokens validate |
| undefined-custom-props | P1 | confirm declared elsewhere → add fallback or declaration; NEVER mass-define |
| dark-coverage (tokens, no dark theme) | P1 | THEMING workflow: derive dark over semantic layer |
| theme-parity | P1 | fill missing theme token from brand map, re-check contrast |
| button-variants / card-duplication | P1 | inventory all → pick canonical (most-used/most-correct) → migrate call sites AST-per-file → delete dupes when 0 refs |
| hardcoded-color / rgba | P2 | hex→existing token by exact match; near-match (#3f5f7f≈#457b9d) = design decision (pick+record); no token yet = create semantic first (3-tier rule) |
| spacing-scale / type-scale / radius-scatter | P2 | snap to nearest scale step (≤2px delta = silent, larger = note); emit changelog per file |
| duplicate-declaration | P2 | drop earlier decl (dead) |
| important-spam | P2 | remove innermost override chain by cascade fix (specificity down / layer), per-file, run visual check |
| transition-all | P2 | name properties (or token durations) |
| inline-styles | P2 | move repeated → class; one-off layout = legit, leave |
| unused-custom-props / duplicate-value | P2/P3 | delete only with 0 refs repo-wide (grep first); duplicates → alias |
| contrast-review | P2 | MANUAL: compute AA per theme; automated browser pass = accessibility skill axe |
| reduced-motion absent | P2 | gate motion tokens w/ media query (web) or setting (game) |

## Fix mode protocol (FIX)

1. Baseline: run project's own checks (typecheck/lint/tests) + screenshots of
   touched routes if tooling exists (testing.md). Record failures as
   pre-existing.
2. Batch: one rule-family per batch, ≤ ~10 files. Structural edits (props,
   imports, JSX) via AST tools (ast-grep/LSP) or exact-match edits —
   repo-wide sed/regex on source = forbidden.
3. After each batch: typecheck + touched tests + visual diff on affected
   screens. Regression → stop batch, fix cause, don't continue dirty.
4. Token edits: source only; regenerate build; diff generated = intended-only.
   Component migration keeps old API alive only during window, thin re-export
   marked with delete date.
5. Close: re-run `ds.mjs audit` → findings delta IS the report; new findings
   = your regressions to fix.

## Triage priorities
P0 everything first · P1 themes+duplication next · P2 mechanical (auto) then
judgment · P3 batch or skip-with-note. Effort tags: S=mechanical minutes ·
M=per-component · L=cross-cutting (design decision + staged migration,
migration.md).
