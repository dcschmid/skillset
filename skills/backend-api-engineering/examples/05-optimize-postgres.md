# Example 5 — optimize Postgres queries

Task: "orders list is slow." Mode OPTIMIZE (performance.md).
Baseline: p95 610ms, k6 25VU seeded 10k rows, `EXPLAIN (ANALYZE BUFFERS)`
→ Seq Scan on orders (missing tenant index) + N+1 line fetches (101 stmts).

1. Index: `CREATE INDEX CONCURRENTLY idx_orders_t_owner ON
   orders (tenant, owner_id, created_at desc) WHERE deleted_at IS NULL`.
2. Lines: single `... WHERE order_id = ANY($1)` + in-code regroup
   (101→2 statements).
Re-measure same conditions: p95 78ms, buffer hits −82%. Table per
performance.md; plan files committed to the change note; index migration
expand-and-contract + `migration-review.sh` clean. Query-count guard test
added (≤3 stmts/request) so the win can't rot.
