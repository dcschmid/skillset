# Quality Metrics & Baselines

Metrics exist to prove deltas. No measurement base → N/A. No invented scores.

## Metric sources (measured vs proxy)

| Metric | Source | Class |
|---|---|---|
| files/lines/code-lines | `collect_metrics.py` | measured |
| max nesting depth | `collect_metrics.py` | measured (indent/brace) |
| branch points, `complexity_proxy` | `collect_metrics.py` | proxy — labeled |
| certified cyclomatic/cognitive CC | language tools only (ruff, clippy, golangci, ESLint complexity, Sonar) | measured if tool ran |
| clone groups | `detect_duplicates.py` | candidates |
| debt markers TODO/FIXME | `collect_metrics.py` | measured |
| coverage / typecheck / lint counts | project's own tools via `verify_changes.py --cmd` | measured if run |
| benchmark numbers | project harness | measured, protocol in performance-analysis.md |

## Baseline workflow

```
before:  verify_changes.py . --save-baseline -o base.json --cmd "<check1>" --cmd "<check2>"
         collect_metrics.py . -o metrics-before.json
after:   verify_changes.py . --baseline base.json --cmd "<same cmds>"
         collect_metrics.py . -o metrics-after.json
         compare_baseline.py metrics-before.json metrics-after.json -o delta.md
```

Same commands, same environment, or the delta is meaningless.

## Quality gates (per work package)

- no NEW check failures vs baseline (pre-existing allowed, listed)
- no unintended public-API change (signature diff)
- no new P0/P1 finding introduced
- no unexplained behavior diff
- no measured perf regression beyond the project's stated budget

## Optional score (project heuristic, transparent formula)

`score = f(hotspot_count, clone_groups, debt_markers, failing_checks)` —
publish the formula next to the number or omit the score. Scores without a
published formula are forbidden.
