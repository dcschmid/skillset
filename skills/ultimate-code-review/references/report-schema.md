# Report & finding schema contract

Machine truth: `schemas/finding.schema.json`, `schemas/report.schema.json`;
executable form: `scripts/validate_findings.py` (keep in sync — script wins
on drift because it is what gates run).

Lifecycle: agents emit `findings-<axis>.json` → merge `findings.json` →
`validate_findings.py` (schema, dedupe, gate) → `generate_report.py`
(md/json/both). Reports render ONLY validated bundles; VALIDATED/PARTIAL
render, INVALID stops with a message.

Honesty invariants the renderer enforces:
- Standards and Spec are separate sections, each with its own counts.
- Skipped axes print "SKIPPED — documented gap, not a pass".
- Declared project checks print "NOT EXECUTED by this report" unless the
  testing agent pasted real output.
- No cross-axis total score exists anywhere in md or json.
- Gate block lists ids + reasons; `invalid` lists rejected findings.

Naming/paths: default output `reports/code-review/` inside the reviewed
project IS allowed (explicit artifact), everything else stays untouched.
Configurable: `--out` dir, `--format`, `--title`; JSON stays parseable
either way. Secrets: findings carry kind+location, values masked.
