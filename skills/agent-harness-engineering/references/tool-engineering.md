# Tool Engineering

Portable contract: `schemas/tool.schema.json`. Machine checks:
`scripts/validate_tools.py`. These deepen both.

## Design gates

- Name: stable, explicit, lowercase (`read_file`, `run-checks`); rename = breaking.
- Description: ≤60 words, single purpose, states when NOT to use it.
- Input: JSON Schema, root `object`, narrow properties, every parameter
  described; type validation on the boundary, not in the model.
- Output: observation contract (observation-and-context.md); stable shape.
- Timeout: always bounded (`timeout_ms`); missing bound is a finding.
- Idempotency: declared; re-run after unknown outcome must be safe or flagged.
- Error handling: every failure path returns the error contract with
  category, cause, retryable, max_retries, stop_condition.

## Granularity ladder (from ECC, extended)

| Tier | Shape | Approval |
|---|---|---|
| **micro** | one controlled action: permission change, deploy, migration | explicit approval; smallest blast radius |
| **medium** | normal loops: read, search, edit, validate | default autonomy inside project bounds |
| **macro** | merged hot-path workflow to cut round-trip cost | inherits the tier of its riskiest step — macro NEVER bypasses approval gates or permission limits |

Promote medium→macro only when round-trip overhead dominates AND the sequence
repeats; keep the component steps observable (sub-steps in trace).

## Audit checklist (what security_scan/audit_harness flag)

duplicate names • identical descriptions • unused tools • missing input
validation • dangerous defaults (no timeout, `--force`, wildcard paths) •
uncontrolled shell • over-broad permissions • missing error contract •
avoidable calls (same call twice without state change) • unstructured output
(model must parse prose to find the result).
