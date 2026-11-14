# Workflow: AUDIT_AND_FIX

Audit an existing project, then fix — prioritized, verifiable steps. The only
mode that changes code by default; `references/safe-auto-fix.md` binds every
edit. Cap: `max_refine_iterations` (default 2).

1. **Baseline.** `git status` (respect uncommitted/foreign changes, build on
   top), discovery output (`project-discovery.md`), build/test status, token
   snapshot, baseline screenshots where a browser exists
   (`visual-regression.md`).
2. **Diagnose** via AUDIT spine (`existing-project-audit.md`) — findings with
   severity · user-impact · design-relevance · tech-risk · effort.
3. **Plan.** P0 critical functional/a11y · P1 significant UI/UX/responsive ·
   P2 generic patterns + inconsistencies · P3 optional polish. Design-only
   brief with functional P0s → document P0s, fix design-domain only.
4. **Implement** P0→P3: smallest reversible diffs, existing tokens/components/
   CSS architecture, semantic HTML, no new deps, no rewrite where a patch
   works. One batch per logical finding-group; verify per batch (build/tests/
   spot render), not just at the end.
5. **Verification.** project build/typecheck/lint/tests + a11y handoff
   (`accessibility` skill) + navigation/critical flows + responsive +
   visual regression pairs (`visual-regression.md`: intended/regression/
   dynamic/technical; regressions → fix or revert that batch).
6. **Final review.** re-run detection engine on touched surfaces; before/after
   score table (real numbers, partial where no render); report per
   `audit-report-format.md`: fixed files, open issues, test results, new gate,
   limitations.
