# lean-engineering

Avoid unnecessary abstractions, dependencies, and configuration during implementation and refactoring. Preserve requirements and architecture that the project needs.

Profile: Private and Working. Preparation: Describe the task, existing interfaces, and constraints. Choose lite, full, ultra, or off to set the intensity.

Expected result: A complete implementation or audit with concrete simplifications and reasons for keeping necessary structure.

Requirements and limits: Do not cut security, validation, persistence, performance, accessibility, or necessary tests. Restate the desired mode when the host does not retain session state.

## lean-engineering: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh lean-engineering
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the lean-engineering skill. Use lean mode full. Add CSV export to existing reports. Reuse installed libraries and preserve authorization and error handling.
```

**Codex:**

```text
Use the lean-engineering skill. Audit src/ for unnecessary abstractions. Also explain which structures should stay because they satisfy real requirements.
```

**oh-my-pi:**

```text
Use the lean-engineering skill. Simplify the configuration parser without changing behavior. Preserve the file format and public API and check existing error cases.
```

## lean-engineering: Self-test

Run from the repository root:

```bash
python3 skills/lean-engineering/tests/test_skill.py
```

## lean-engineering: Modes and commands

Modes `lite`, `full`, `ultra`, and `off` set the intensity. Commands such as
`/lean review`, `/lean audit`, `/lean simplify`, `/lean debt`, `/lean status`,
and `/lean help` name workflows. If the host has no registered slash command,
spell out the skill name and task instead.

## lean-engineering: Collaboration and limits

During collaboration, project rules and domain requirements remain binding.
These limits also apply in ultra mode: a smaller diff does not justify removing
validation or error handling.

## lean-engineering: Troubleshooting

If a new session does not retain the mode, state it again. Installation and
examples appear above. An audit can also explain why an apparently complicated
structure is necessary.

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [tests/](tests/): Self-tests and fixtures.
