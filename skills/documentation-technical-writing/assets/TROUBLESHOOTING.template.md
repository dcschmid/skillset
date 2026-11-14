# Troubleshooting — <project-name>

Only reproduce-then-record entries. Format: symptom → verified cause → fix that was run.

## <area: install | run | build | deploy | tests>

### <error text as observed, first line only>

Cause: <what was actually wrong, from the fix commit/diff if available>

Fix:

```
<the command or config change that resolved it>
```

Verified: <date/version context where this held>.

## Diagnostic commands

| Question | Command | Reading the output |
|---|---|---|
| Which version? | `<cmd>` | <what field matters> |
| Config loaded? | `<cmd>` | <expected shape> |

## Escalation

Unresolved here: attach <log file path>, <command output>, environment (<OS, runtime version>).
