# Performance Analysis

Performance claims need measurements; otherwise they are hypotheses, labeled.

## Detection signals (static, hypothesis-grade)

- Loops over collections inside loops (N+1 shape) — grep nesting + call.
- Repeated identical calls in one scope (recomputation).
- Per-frame allocations in game update paths (Lua tables/GDScript arrays in
  `_process`, JS object churn in render loops).
- Awaiting in sequential loops where `Promise.all`/`gather`-style batching
  preserves semantics.
- Sync I/O on hot paths; JSON round-trips used as clone.

These are CANDIDATES. Correctness-preserving but measurement-unproven notes
stay "hypothesis".

## Measurement protocol (when optimizing is approved)

1. Pin environment: same machine, quiescent, same data size.
2. Same command N≥5 runs, report median; tool: project benchmark harness if
   present, else a timing script written next to the touched code (deleted
   after, unless the project wants it kept).
3. Dimensions: wall time, allocations, GC pauses, CPU, I/O, startup, bundle
   size (web), frame time (games), load times.
4. Before/after table in the report — measured numbers or N/A.

## Restraint

Premature optimization is debt with extra steps. Optimize when: profiled hot
path, or documented budget (frame time, p95 latency, bundle size) exists.
"Looks faster" edits without a budget = refused.

Game-specific: frame-time budgets come from the engine (30/60/120 fps
targets), memory ceilings from platform; validate on the engine's own
profiler output, never on generic web heuristics.
