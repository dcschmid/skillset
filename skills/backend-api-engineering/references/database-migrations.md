# Safe Database Migrations

Load for modes DATABASE / MIGRATE / AUDIT. Governs live-schema change.

## Non-negotiables

- Prod execution needs explicit approval; author+test on scratch/CI DB.
- No prod data for tests. Never drop/reset without approval (hard stop).
- Every migration: up + down, or up + written forward-fix; versioned in the
  project's tool (Alembic/Django/Flyway/Prisma/Drizzle/knex/EF/Goose/…).
- `scripts/migration-review.sh <dir>` lints destructive DDL + ordering.

## Expand-and-contract (default for live systems)

1. **Expand:** add nullable column / new table / new index (CONCURRENTLY).
   Deploy code that writes both, reads old.
2. **Backfill:** batched (keyset chunks, sleep between), idempotent,
   resumable, monitored (row counts + lag). Not inside the DDL txn.
3. **Switch reads:** flip code to new shape behind deploy; verify parity
   counts.
4. **Contract (separate later deploy):** drop old column/table only after
   all writers migrated; lock timeout set; run during low traffic.

One deploy step per phase — never add+backfill+drop in one migration.

## Change recipes (lock/time risk)

| Change | Safe path |
|---|---|
| add column NOT NULL default | nullable + backfill + set not null (validated), or default without rewrite (PG11+) |
| rename col/table | view or dual-write window; `RENAME` is cheap on PG but breaks old code deploys → 2 deploys |
| change type | new column + copy + swap; never `ALTER TYPE` on hot wide table without measurement |
| add unique/index | CONCURRENTLY / online; duplicate handling pre-checked |
| PK/FK change | new constraint `NOT VALID` → validate; or shadow table + swap for huge tables |
| drop column/table | only after readers/writers migrated; soft-drop first where value justifies |

## Checks before running anywhere

backup taken/restore tested · migration dry-run (tool `--sql`/offline mode)
· estimated rows touched + runtime · locks held (level+duration) ·
backward compat with running old code · idempotent re-run safe · data-loss
review for nullable→not-null and truncation · CI run against engine+version
from the project's compose/test config.

## Rollback vs forward-fix

Small: down migration. Large/backfilled: forward-fix plan (old shape kept
one release; documented restore point). State which before running.

## Tests that belong to the change

migration up on empty DB · up on populated fixture (row count + checksum
asserts) · down/up round-trip where promised · app boots + touched queries
pass against new schema · backfill idempotency re-run.
