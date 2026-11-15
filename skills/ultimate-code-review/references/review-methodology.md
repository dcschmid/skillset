# Review methodology

## Axis independence
Six axes, six verdicts. A change can pass Standards and fail Spec (right
conventions, wrong feature) or pass Spec and fail Standards (right feature,
foreign style). Merging them into one score hides exactly the signal a
review exists to produce. Aggregation only counts and links; never reranks
across axes. The one shared surface allowed: a release-blocker list that
lists each blocker with its home axis intact.

## Orchestration contract
- Depth 1. Axis agents never spawn agents and never re-invoke this skill —
  a review skill that recurses produces reports about reports.
- Fresh context per axis: each agent gets its brief (`agents/<axis>.md`),
  the scope bundle, the diff, and the sources ITS axis needs — nothing that
  biases it toward another axis's verdict.
- Every agent works on the same immutable snapshot (scope.json SHAs). No
  agent re-diffs mid-review.
- Missing runtime parallelism → sequential passes, same briefs, same schema;
  the report says sequential. Claiming parallel agents you didn't run is a
  fabricated result.
- Partial failure: one axis agent dies → its axis joins skipped-axes with
  the reason; the report still renders (PARTIAL), gate stays honest.

## Full-repo mode (`--full`)
Inventory → prioritize (entry points, changed-hot, public APIs, tests) →
bounded batches. Completeness claim allowed only over what was covered;
remainder is Limitations. A "full review" of 10% is PARTIAL.

## Loading discipline (progressive disclosure)
SKILL.md spine always; agent brief when its axis runs; a references/ file
only when the axis needs the depth. Reports cite, they don't restate docs.
