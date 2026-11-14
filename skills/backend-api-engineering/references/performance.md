# Performance Engineering

Load for modes OPTIMIZE / AUDIT. Law: **measure → change → re-measure.**
No baseline ⇒ no optimization claim (`NOT TESTED`).

## Measure first (pick the narrowest honest instrument)

- **API latency:** p50/p95/p99 from project metrics, or wrk/k6/hey against
  a local/CI stack; fixed concurrency, fixed dataset, ≥3 runs, warm caches
  stated. Same conditions before/after.
- **DB:** `EXPLAIN (ANALYZE, BUFFERS)` diff (see database-engineering.md);
  query count per request (ORM logs) for N+1.
- **Process:** CPU/RSS (container limits), event-loop lag (Node
  `perf_hooks`), GC pauses, thread pool waits, pool acquire p95.
- **Cache:** hit/miss ratio + eviction; stampede evidence = concurrent
  misses on one key.
- **Queues:** oldest-job age, processing p95, retry rate.
Payload bytes and serialization time when responses are the cost.

## Optimization ladder (cheapest first)

1. Kill N+1 / unbounded fetches → batch, join, cap page size.
2. Index + query shape (plan-verified) before touching code.
3. Cache: response/fragment (ETag), server-side (Redis) with explicit TTL
   + invalidation; single-flight for hot-key stampedes.
4. Serialize less: DTO field trimming, compression (gzip/brotli at proxy),
   pagination/cursor, column pruning.
5. Move work off the request: job queue (background-jobs-messaging.md),
   streaming for large exports.
6. Pool + concurrency config: DB pool, HTTP client pools, worker count —
   document sizing math.
7. Runtime: connection reuse (keep-alive), prepared statements, async I/O
   where the stack supports it; CPU work → native/compiled or offloaded.

## Reporting format (mandatory)

```
metric | baseline | after | method+conditions | delta | status
GET /orders p95 340ms → 90ms | k6 25 VU, 10k rows, warm | -74% | VERIFIED
```
Cache-hit %, rows scanned, or query count replace wall-clock where more
honest. Confounders (cold start, smaller dataset, different host) named;
incomparable runs compared only qualitatively.

## Anti-patterns the skill calls out

premature caching (staleness bugs), index on every column, `SELECT *`,
retries as perf strategy, benchmarking on prod, horizontal scaling to hide
one missing index, async for I/O-less code, micro-benchmarks presented as
production numbers.
