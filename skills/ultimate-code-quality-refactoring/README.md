# ultimate-code-quality-refactoring

Find complex code, duplication, dead code, and problematic module boundaries. Preserve behavior during refactoring and verify each step against a baseline.

Profile: Private and Working. Preparation: Specify directories or files, audit versus implementation, and public interfaces that must remain stable.

Expected result: Evidence-backed findings or a verified refactoring with focused steps, preserved behavior, and documented limits.

Requirements and limits: Audits are read-only by default. Major architecture changes need a decision. Keep bug fixes and new features distinct from behavior-preserving refactoring.

## ultimate-code-quality-refactoring: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh ultimate-code-quality-refactoring
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the ultimate-code-quality-refactoring skill. Audit src/ for technical debt. Identify concrete files and prioritize maintenance risks. Do not edit code yet.
```

**Codex:**

```text
Use the ultimate-code-quality-refactoring skill. Simplify packages/core/pricing.ts without changing behavior. Preserve the public API and run existing tests after each meaningful step.
```

**oh-my-pi:**

```text
Use the ultimate-code-quality-refactoring skill. Investigate the duplicated parsers. Check their differences first and consolidate only if existing contracts can be preserved.
```

## ultimate-code-quality-refactoring: Self-test

Run from the repository root:

```bash
python3 skills/ultimate-code-quality-refactoring/tests/test_skill.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [assets/](assets/): Support files and templates.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [collect_metrics.py](scripts/collect_metrics.py)
- [compare_baseline.py](scripts/compare_baseline.py)
- [detect_duplicates.py](scripts/detect_duplicates.py)
- [detect_project.py](scripts/detect_project.py)
- [generate_report.py](scripts/generate_report.py)
- [run_audit.py](scripts/run_audit.py)
- [verify_changes.py](scripts/verify_changes.py)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/ultimate-code-quality-refactoring` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
python3 scripts/run_audit.py /path/to/project --quick
```

## Understand the baseline

`run_audit.py` leaves the target project unchanged and writes its audit bundle
to `/tmp` by default. `--quick` skips duplicate detection; remove the flag for a
full run. Complexity proxies identify code to investigate, rather than measuring
runtime performance.
