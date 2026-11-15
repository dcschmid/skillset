# Audit a deliberately flawed agent harness

`agent.py` and `tools.json` contain intentional problems. Use them to see how
the auditor derives findings from actual files. From the repository root:

```bash
python3 skills/agent-harness-engineering/scripts/audit_harness.py --project skills/agent-harness-engineering/examples/audit-example --format json
```

Look for these cases:

- `API_KEY` is inserted into the prompt and can reach context and traces.
- `except Exception: pass` hides failures. The bounded `while turn < 10` loop is not an unbounded loop.
- Duplicate tool names and identical descriptions make tool selection ambiguous.

Categories without observable evidence are skipped with a reason and excluded
from scoring. Automatic JSON cleanup is separate from proposed code fixes:
this fixture has no independent executable behavior test. Work on a copy when
experimenting rather than changing the committed fixture.

```text
Use agent-harness-engineering. Explain this example's findings, then check
our harness for the same issue classes. Report only.
```

Return to the [skill README](../../README.md).
