# Ultimate Code Review & PR Audit

Multi-axis, evidence-backed review of diffs and whole projects. Read-only by
default; Standards and Spec never merge; skipped checks stay gaps.

## What it does
Six independent axes — Standards, Spec, Bugs/Regression, Security, Testing,
Performance/Architecture — over any git baseline (branch/commit/range/staged/
untracked/file/full/PR), stack-agnostic (web, backend, Godot/Defold/Blender,
CLI, monorepos, IaC). Findings: `file:line` + quoted evidence, severity ×
confidence, schema-validated, deduped. Optional gates, optional `--fix`.

## Requirements
- Python 3.8+ (scripts stdlib-only), git. Optional: `gh`/`glab` (PR metadata,
  read-only), project's own linters/tests (used as evidence, never assumed).

## Install (this repo)
`tools/install-skills.sh ultimate-code-review` → symlinks into
`~/.claude/skills` + `~/.agents/skills`; omp loads both. Uninstall:
`tools/uninstall-skills.sh ultimate-code-review`.

## Invocation (Claude Code / Codex / omp — natural language, flags are intent)
- `/code-review` · "review since main" → merge-base…HEAD (**three-dot**)
- `--base develop` `--commit HEAD` `--range HEAD~5..HEAD` (two-dot, direct)
- `--uncommitted` `--staged` (untracked listed separately, never doubled)
- `--file path` · `--full` (batched inventory; incomplete ⇒ PARTIAL)
- `--spec docs/sprint-14.md` · no spec ⇒ `SPEC_NOT_AVAILABLE`, never invented
- `--fix [--safe-only]` — the ONLY write mode; `--safe-only` refuses
  architecture/migration/auth churn. No commit/push ever without approval.
- `--report md|json|both` → `reports/code-review/` (configurable)
- `--gate critical|high|security|all` → exit 0 pass / 1 blocking / 2 config

Agents without slash commands use the phrases; behavior identical.

## Direct automation
```bash
S=skills/ultimate-code-review/scripts
python3 $S/prepare_review.py -w /tmp/ws PROJECT -- --base main
python3 $S/validate_findings.py /tmp/ws/findings.json -o /tmp/ws/v.json --gate high
python3 $S/generate_report.py /tmp/ws/v.json --format both -o DIR
```

## Architecture
`SKILL.md` spine → isolated axis briefs (`agents/`) → `scripts/` validate+
report. Depth-1, no recursion; sequential fallback labeled honestly. CI:
example in `assets/` wiring; opt-in only. Details: `references/`.

## Limitations
Judgment layer is the host model — determinism lives in the scripts. Large
repos review in batches (PARTIAL beats fake "full"). PR platforms read-only;
posting stays with `review-followup` + user approval.

## Troubleshooting
Bad ref → fix the ref (report is blocked by design) · NEEDS_BASE_REF → pass
`--base` · gate fails with skipped axes → gaps listed, not failures ·
fix-mode test failure → fix not counted; revert own hunks.

## Attribution
Concept lineage (axis independence, merge-base discipline, smell baseline)
from Matt Pocock's `code-review` skill (MIT License, github.com/mattpocock/
skills) — extended, not copied; no source files duplicated.

Self-test: `python3 skills/ultimate-code-review/tests/test_skill.py`.
