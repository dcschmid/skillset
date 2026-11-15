# Check supervisor and worker handoffs

`config.json` declares delegation. The auditor evaluates what it can observe
in configuration or traces. Missing evidence produces a reasoned skip.

From the repository root:

```bash
python3 skills/agent-harness-engineering/scripts/audit_harness.py --project skills/agent-harness-engineering/examples/multi-agent --only multi-agent
```

A healthy recorded flow can look like this:

```json
{"steps": [
  {"kind": "handoff", "name": "supervisor->worker_a", "arguments": {"task": "t1"}, "ok": true},
  {"kind": "tool_call", "name": "write_file", "arguments": {"path": "out/a.md"}, "ok": true},
  {"kind": "handoff", "name": "worker_a->supervisor", "arguments": {"task": "t1", "artifact": "out/a.md"}, "ok": true},
  {"kind": "handoff", "name": "supervisor->worker_b", "arguments": {"task": "t2"}, "ok": true},
  {"kind": "tool_call", "name": "validate", "arguments": {"path": "out/a.md"}, "ok": true}
]}
```

Save this to a new JSON file for an exercise and pass its path to
`scripts/detect_loops.py` from the skill directory. Repeated handoffs with
identical arguments can indicate a delegation loop; findings should identify
the affected steps.

Only worker_a writes `out/a.md`; the validator reads it. See
[multi-agent.md](../../references/multi-agent.md) for the shared-state rules.

```text
Use agent-harness-engineering. Analyze our recorded flow for repeated
handoffs and competing writes. Do not start agents.
```

These are analysis requests usable in all three clients; they do not activate
delegation. Return to the [skill README](../../README.md).
