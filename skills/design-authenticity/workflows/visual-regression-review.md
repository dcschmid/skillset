# Workflow: VISUAL_REGRESSION_REVIEW

Did recent changes break surfaces? Compare before/after, find unintended
change, fix regressions (or report them when review-only was requested).

1. **Change inventory:** `git diff`/commits in scope → touched routes,
   components, tokens; select affected routes/states.
2. **Capture pairs** under parity (`visual-regression.md`): viewports, themes,
   data state, frozen animations, fonts ready. Existing baselines from
   AUDIT_AND_FIX reused; none → capture "before" from pre-change revision if
   checkout-able, else declare source-diff-only review.
3. **Classify diffs** intended/regression/dynamic/technical; inspect renders
   for overflow, overlap, clipped text, lost states, broken dark mode,
   responsive collapse.
4. **Verdict** PASS / FAIL(+pairs) / NOT AVAILABLE — never fabricated.
5. **Repair:** regressions are P1 fixes under `safe-auto-fix.md`, re-captured.
   Review-only task → findings + patch proposals, no code changes.
6. Report section per `audit-report-format.md` § 10/11.
