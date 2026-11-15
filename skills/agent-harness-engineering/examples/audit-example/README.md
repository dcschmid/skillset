# Example: a harness with findings — what the audit reports and why.

`audit-example/agent.py` is a deliberately imperfect agent loop. Run:

```bash
python3 scripts/audit_harness.py --project examples/audit-example --format json
```

Expected finding classes (deterministic, from real file content):

- **security** — `API_KEY` interpolated into the prompt string (secret into
  every trace/context).
- **reliability** — `except Exception: pass` swallow (silent failure); the
  `while turn < 10` loop is bounded, so it is NOT flagged.
- **tools** — duplicate `read` name + identical descriptions (ambiguous
  selection); de-duplication ships as a LOW-risk fix via `--apply`.

Score: categories with no observable material (performance, multi-agent) are
`skipped` with a reason and excluded from the 0..100 denominator. Auto-fix
applies only the JSON de-dup; every code fix stays a documented proposal
because the example ships no runnable test of its own.
