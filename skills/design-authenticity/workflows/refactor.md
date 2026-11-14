# Workflow: REFACTOR

Improve an existing design while preserving behavior. Smallest change that
fixes the identified problems; no unasked full redesign.

1. **Preservation inventory.** What must not break: tokens consumed elsewhere,
   components in use, interaction/behavior, a11y already in place, project
   config/stack rules. Diff-scope = what the task named.
2. **Diagnose** via REVIEW steps 1–4 (same engine), plus: which findings are
   fixable INSIDE the existing system vs needing token change. Prefer inside.
3. **Plan** per finding: file, change, why product-fit, risk to preservation
   list. Token edits: stated reason + migrated consumers listed.
4. **Apply** in the project's stack (`framework-integration.md`). No new deps,
   no parallel token system, no behavior edits; tests stay green (project suite).
5. **Regression.** Render before/after if possible (`scripts/
   screenshot_audit.sh`): diff proves CHANGE only — judge with
   `visual-quality-gates.md`; rerun detection engine on touched surfaces; a11y
   handoff unchanged or better.
6. **Report.** per finding: fixed/improved/kept + evidence; iteration cap
   honored; residual open issues listed, not hidden.

Guarantees: features keep working; existing brand tokens survive unless the
task was an explicit redesign; untouched surfaces untouched.
