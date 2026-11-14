# Workflow: REVIEW

Audit an existing design WITHOUT changing code. Output = findings report.

1. **Scope.** Which routes/components/states; light/dark; viewports. Prefer the
   rendered product (dev/preview server + `scripts/screenshot_audit.sh` or repo
   browser tooling). Render unavailable → source-level review, header states
   "source-only, VISUAL_REVIEW_REQUIRED for visual axes". Never emit a numeric
   visual score without a render.
2. **Context.** Read tokens/brand/direction + any `profiles/<project>.md` named
   in the task. "Deliberate?" questions resolve here first.
3. **Detect.** `references/anti-ai-patterns.md` categories A–J. Reproduce every
   observation (selector/value/count) before filing. One finding per root cause.
4. **Classify.** real-problem / deliberate-choice / constraint / taste — per the
   engine's filter. False-positive discipline binding: a correct card is not a
   finding.
5. **Report.** `examples/design-review.example.md` frame: findings ordered by
   severity, each with component/observation/rationale/fix(+before-after);
   optional rubric snapshot (only from real renders); NOT TESTED lines for
   anything unverified.

No file modifications. Fixes are proposed, not applied — applied fixes move to
REFACTOR.
