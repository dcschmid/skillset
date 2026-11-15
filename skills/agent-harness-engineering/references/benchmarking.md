# Agent Benchmarking & Evaluation

Machine checks: `benchmark_agent.py` (runner), `compare_benchmarks.py`
(before/after). Schemas: `schemas/benchmark-result.schema.json`.

## Metrics (reported or honestly marked unavailable)

task completion rate • pass@1 • pass@3 (needs `runs_per_task ≥ 3`) • retry
count • tool calls/task • tool error rate • loop detection rate • recovery
success rate • duration • token usage (estimate unless platform reports) •
cost per success • security violations • result quality (needs grader; else
UNVERIFIED).

## Honesty contract (binding)

- **offline mode** scores recorded traces — it is explicitly labeled
  `recorded-trace (offline; NOT a live run)`.
- **adapter mode** runs a documented runner command; no adapter ⇒ the run
  refuses, it never fabricates a live number.
- Missing trace/adapter result ⇒ task `UNVERIFIED`, counted separately;
  never guessed 0/false.
- Mode mismatch (offline vs live) ⇒ compare_benchmarks answers
  `NOT COMPARABLE`, not "improved".
- Model variance: repeated runs required for pass@k; single runs report
  pass@1 with `runs_per_task` shown.

## Depths

`quick` (local deterministic checks) · `standard` (functional + reliability
suites) · `deep` (adds failure injection, recovery, security, performance).
Same suite, same tasks across depths — only check depth changes.

## Before/after

Same mode + same suite = comparable; report shows per-metric Δ and flags
regressions. Mock vs mock is comparable; mock vs live is not.
