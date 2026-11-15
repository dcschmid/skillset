# Example: supervisor → workers, and the audit answers for multi-agent.

`config.json` declares delegation; `audit_harness.py --only multi-agent`
answers only from observable material — no delegation config ⇒ category
`skipped` (never a fake zero). Trace shapes below feed `detect_loops.py`.

Healthy handoff trace (`detect_loops.py` → PASS):

```json
{"steps": [
  {"kind": "handoff", "name": "supervisor->worker_a", "arguments": {"task": "t1"}, "ok": true},
  {"kind": "tool_call", "name": "write_file", "arguments": {"path": "out/a.md"}, "ok": true},
  {"kind": "handoff", "name": "worker_a->supervisor", "arguments": {"task": "t1", "artifact": "out/a.md"}, "ok": true},
  {"kind": "handoff", "name": "supervisor->worker_b", "arguments": {"task": "t2"}, "ok": true},
  {"kind": "tool_call", "name": "validate", "arguments": {"path": "out/a.md"}, "ok": true}
]}
```

Pathological: `supervisor<->worker` repeating with identical arguments ⇒
`delegation loop` finding with the indices, not a shrug. Shared-state rule
(references/multi-agent.md): one writer per artifact; here `out/a.md` is
written only by worker_a, validator is read-only.
