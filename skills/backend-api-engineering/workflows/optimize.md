# Workflow: optimize (latency/throughput/cost)

Input: "slow", p99 target, load report, or measured bottleneck. Output:
before/after evidence + landed change. No baseline ⇒ no claim.

1. **Define the SLI** (endpoint p95, query count, queue lag) and the
   budget. Instrument/read what exists before adding anything.
2. **Baseline** under stated conditions (dataset, concurrency, warm/cold,
   host) — performance.md format, ≥ comparable runs. Profile hot path:
   DB (`EXPLAIN ANALYZE`, counts), process (CPU/RSS/event-loop/pools),
   payload, network, cache hit rate.
3. **Rank by cost × risk**, apply the performance.md ladder bottom-up:
   queries/indexes (plan-verified) → batching/N+1 → cache+single-flight →
   payload/serialization → offload to jobs → pool/concurrency config.
   Each step one change, one measurement.
4. **Re-measure same conditions.** Report table per performance.md; deltas
   without confounders, confounders named. Regression either reverted or
   documented with cause.
5. **Keep the instrument** (test/assert/query-count guard/CI perf budget
   where the project has one) so the win can't silently rot.
Approval gates unchanged: benchmarking runs local/CI only, no prod load,
no prod data for fixtures.
