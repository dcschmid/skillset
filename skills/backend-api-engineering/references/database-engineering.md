# Database Engineering

Load for modes DATABASE / OPTIMIZE / AUDIT / CREATE. Engine-agnostic rules +
per-engine pointers. Project's ORM stays; raw SQL fine when better.

## Schema design

- **Keys:** surrogate or domain PK, consistent type across schema; FKs
  always declared with explicit ON DELETE/UPDATE. Nullable only with a
  stated reason; `NOT NULL + default` otherwise.
- **Constraints in DB, not only app:** unique, check, enum-as-table-or-
  native-enum. The DB is the last honest layer.
- **Normalization** to 3NF by default; denormalize only with a named read
  pattern + measured write cost. Document denormalized columns + refresh
  path (trigger/job/app hook).
- **Timestamps** `timestamptz`/UTC; soft-delete with index-aware `deleted_at`
  or `status`, applied consistently — mixed styles = finding.
- **Multi-tenant:** tenant column from day one (see authorization.md).
- **JSON columns** for genuinely schemaless payloads; queried fields get
  generated columns/expressions + indexes instead of runtime JSON walks.

## Indexes

- Index driven by the actual predicate: `(tenant_id, status, created_at)`
  for scoped sorted scans; leading column = equality, trailing = range/sort.
- Covering indexes on hot read paths; expressions indexes for function
  predicates; partial indexes for hot subsets (`WHERE deleted_at IS NULL`).
- Every migration adding an index on a live table: `CONCURRENTLY`
  (Postgres) / online-DDL equivalent; verify with `EXPLAIN (ANALYZE,
  BUFFERS)` before declaring done.
- Unused-index sweep periodically; write amplification is real.

## Query discipline

- **N+1 detection:** ORM lazy-load loops, per-row `await` in list handlers,
  request logs showing N similar queries. Fix: join/batch (DataLoader,
  `select_related`/`joinedload`, `IN (...)` chunks) or denormalized read
  model. Always re-measure: before/after query counts, not vibes.
- Fetch only needed columns; streams/cursors for large exports; bounded
  `IN` lists.
- Transactions: short, one intent; `SELECT ... FOR UPDATE` (pessimistic)
  for counter/inventory, version column (optimistic) for edit-conflict
  handling; document the chosen isolation level, don't leave defaults
  accidental in money paths.
- Connection pools: sized to DB `max_connections` headroom across all
  instances; saturation is an audit metric (p95 acquire wait).

## Diagnostics (evidence before claims)

`EXPLAIN (ANALYZE, BUFFERS)` · pg_stat_statements / slow log ·
`pg_stat_user_tables` seq-scan ratios · lock waits · pool metrics. SQLite:
`EXPLAIN QUERY PLAN`. MySQL: `EXPLAIN ANALYZE`. Record the plan in the
change note; without a plan or numbers the optimization is `NOT TESTED`.

## Redis / document / search / vector

- Redis: explicit TTLs or documented eviction; never sole source for
  durable data; keys namespaced `{app}:{domain}:{id}`; SCAN not KEYS.
- Mongo: schema validation on collections; aggregation pipelines bounded
  (`allowDiskUse:false` default); indexes mirror query shapes.
- Search/vector: index built from primary store, reindexable, staleness
  documented; similarity thresholds + `WHERE` prefilter for tenant scoping.
