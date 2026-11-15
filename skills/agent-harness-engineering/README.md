# agent-harness-engineering

Design, audit, optimize, secure, benchmark, and repair agent harnesses —
the machinery around the model: tools, observations, context, recovery,
coordination, traces. Platform-independent core + deterministic Python CLIs
(stdlib only, python3 ≥ 3.10; no network, no installs).

Related but distinct: **skill-orchestrator** selects and validates *skills*;
this skill engineers the *runtime of agents*. App-code quality/security stays
with the code-focused skills; this skill takes the harness.

## Install

```bash
tools/install-skills.sh agent-harness-engineering   # symlink into host roots
tools/uninstall-skills.sh agent-harness-engineering
```

No dependencies beyond the stdlib. Deep docs in `references/` (router table in
`SKILL.md`), JSON-Schema contracts in `schemas/`, deterministic checks in
`tests/`.

## Workflows

```bash
# audit any project's harness (read-only; score excludes unobservable lanes)
python3 scripts/audit_harness.py --project /path/to/project --format markdown
# fix plan (dry-run, writes nothing) → deterministic JSON fixes only
python3 scripts/audit_harness.py --project /path/to/project --fix
python3 scripts/audit_harness.py --project /path/to/project --apply
# contracts
python3 scripts/validate_tools.py tools.json
python3 scripts/validate_observations.py observations.json
# runtime forensics
python3 scripts/detect_loops.py trace.json
python3 scripts/analyze_traces.py trace.json
python3 scripts/analyze_context.py context-manifest.json
python3 scripts/security_scan.py /path/to/project
# evaluation (offline over recorded traces is always labeled as such)
python3 scripts/benchmark_agent.py bench.json --out after.json
python3 scripts/compare_benchmarks.py before.json after.json
python3 scripts/generate_report.py after.json --out report.md
```

Host invocations: name the skill and the ask — "audit this agent's harness
with agent-harness-engineering and fix safe findings"; "benchmark the tool
calls before/after"; Claude Code (`~/.claude/skills/`), Codex
(`~/.agents/skills/`), omp load the same content. Slash commands only where a
host verifies them — none are promised here.

## Honest results

Skipped categories never distort the score; missing platform token data ⇒
labeled estimates; offline benchmarks never claim live measurement; missing
evidence ⇒ UNVERIFIED. `python3 tests/test_skill.py` (verdict line
`VERDICT: PASS|FAIL`, exit 0/1) proves the machinery end to end, including
dry-run safety, injection surface, retry bounds, and regression detection.
