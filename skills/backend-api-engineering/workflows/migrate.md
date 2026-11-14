# Workflow: migrate (stack/DB/schema, controlled transition)

Input: "move X to Y", schema change, ORM/tool swap, engine upgrade.
Output: phased plan + landed safe phase + tested cutover steps.

1. **Freeze the truth.** Source & target versions from lockfiles/official
   docs (online check when possible); row counts and hot tables from the
   live schema shape (no prod data copies).
2. **Classify the transition:** additive (expand) / replacing (expand→
   backfill→switch→contract, database-migrations.md) / swap (parallel
   run + cut). Each phase separately deployable; old+new coexist window
   defined.
3. **Author migrations** in the project's tool: up+down or forward-fix;
   `scripts/migration-review.sh` on the dir; dry-run (`--sql`) + run on
   scratch seeded DB; lock/runtime estimate stated.
4. **Data movement:** batched keyset jobs, idempotent, resumable,
   parity-checked (counts+checksums); progress surfaced in logs/metrics.
5. **Code migration:** adapters/strangler at boundaries, feature-scoped
   flips, not big-bang rewrites; specs updated (`validate-openapi.py
   --baseline`) and clients regenerated in CI.
6. **Verify:** migrations up/down on seeded DB, touched-query suites,
   parity asserts, boot + `/readyz`. Then hand prod execution (approval)
   and contract-drop phase (later deploy) to the owner with the runbook.
