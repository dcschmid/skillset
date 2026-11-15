# skill-orchestrator

Inventory actual skills, validate their structure, and investigate overlap. Produce a reasoned skill selection and sequence for a concrete task.

Profile: Private and Working. Preparation: Provide the collection or skill and the requested check. For routing, describe the task and its requirements.

Expected result: A reproducible report, routing plan, or repair proposal with explicit verification limits.

Requirements and limits: Read-only by default. Repairs remain proposals until approved. Agent evaluations that were not run remain UNAVAILABLE; test files do not count as executed tests.

## skill-orchestrator: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh skill-orchestrator
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the skill-orchestrator skill. Audit this skill collection using the portable profile. Report structural errors, overlaps, and areas you could not evaluate.
```

**Codex:**

```text
Use the skill-orchestrator skill. Which skills fit an accessible Astro website with localization? Explain selection and order without activating the entire collection.
```

**oh-my-pi:**

```text
Use the skill-orchestrator skill. Check human-writing and documentation-technical-writing for conflicting responsibilities. Propose focused corrections without editing files.
```

## skill-orchestrator: Self-test

Run from the repository root:

```bash
python3 skills/skill-orchestrator/tests/test_orchestrator.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [skill-orchestrator](scripts/skill-orchestrator)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/skill-orchestrator` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
python3 scripts/skill-orchestrator --help
python3 scripts/skill-orchestrator scan
```

## Inventory versus evaluation

The launcher works without package installation and reads the actual collection
files. Check subcommand help before use. A scan inventories files; executing
tests and evaluating agent behavior are separate steps.
