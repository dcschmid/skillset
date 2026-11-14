# Example 6 — safe schema migration (status enum, no downtime)

Task: "add order status without downtime." Mode DATABASE
(database-migrations.md, templates/migration.sql).

Plan (expand-and-contract, 4 deploys): 1 nullable
`status_code smallint` + `migration-review.sh` clean (NOT-NULL-without-
DEFAULT trap avoided by design) · 2 backfill keyset batches 1000, idempotent,
lag metric · 3 switch readers+writers behind flag, parity counts checked ·
4 (later, approval) drop legacy col after old releases retired.
Tests: up on empty+seeded DB, parity asserts, app boots, touched queries
green; `--sql` dry-run output attached. Prod execution: approval requested,
not executed by skill. Rollback: phase 1-2 down migrations; phase 3 forward-
fix documented before running.
