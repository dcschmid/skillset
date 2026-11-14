-- migration template — expand-and-contract unit (one deploy phase each)
-- Phase example: add nullable → backfill → switch reads → (later) constrain/drop.
-- Run through the project's migration tool; dry-run first (`--sql`).

-- UP
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

ALTER TABLE orders ADD COLUMN status_code smallint;  -- nullable: no rewrite
COMMENT ON COLUMN orders.status_code IS 'added <date>, phase 1/4 expand; backfill job: scripts/backfill_status.py';
COMMIT;

-- CONCURRENTLY outside a transaction (run as separate step in the tool):
-- CREATE INDEX CONCURRENTLY idx_orders_status_code ON orders (status_code) WHERE status_code IS NOT NULL;

-- DOWN
-- BEGIN; ALTER TABLE orders DROP COLUMN status_code; COMMIT;
-- (or forward-fix note: keep column, deploy fix <ref>; old shape kept 1 release)
