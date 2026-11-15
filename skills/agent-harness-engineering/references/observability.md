# Observability & Debugging

Machine checks: `analyze_traces.py` (timeline, per-tool stats, error history,
redaction), `detect_loops.py` (anti-patterns over traces).

## Vocabulary (OpenTelemetry concepts, no runtime required)

trace = one task run; span ≈ one agent step/tool call (kind, name, args
digest, ok flag); correlation id passthrough in `metadata`. Where a real OTel /
platform tracer exists, adapt its export into the trace JSON shape these tools
read — never invent spans it did not emit.

## Requirements

structured logs • tool-call + agent-step tracing • error history • runtime
metrics • correlation ids • task states • checkpoint inspection • action
timeline. Without platform metrics, durations/tokens come back as estimates
or unknown — reported as such.

## Privacy

no secrets in traces (analyze_traces.py masks long opaque literals on output);
redact sensitive inputs at the adapter boundary; configurable log levels;
storage location declared; no unsolicited external telemetry.

## Debugging loop

1. record trace of the failing run
2. `analyze_traces.py` → timeline + error history
3. `detect_loops.py` → loop/anti-pattern evidence
4. fix the harness (not the trace), re-record, compare.
