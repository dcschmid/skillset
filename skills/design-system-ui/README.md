# design-system-ui

Create and audit design tokens, themes, and reusable components. Find duplicate colors, inconsistent spacing, and components that bypass the existing system.

Profile: Private. Preparation: Provide the project, token sources, themes, and affected components. Specify audit versus implementation.

Expected result: File-and-line findings, validated tokens, or an incremental migration with documented component contracts.

Requirements and limits: The system follows the project visual identity. The Node tool needs no extra packages. Figma requirements remain binding when Figma is the design source.

## design-system-ui: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh design-system-ui
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude private
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the design-system-ui skill. Audit src/ for duplicate colors, spacing, and button variants. Report file and line and propose a safe cleanup order.
```

**Codex:**

```text
Use the design-system-ui skill. Dark mode is broken in three components. Find token mismatches, fix them, and verify both themes and focus states.
```

**oh-my-pi:**

```text
Use the design-system-ui skill. Create a DTCG token model from our existing palette for light and dark themes. Use a build step and document semantic tokens.
```

## design-system-ui: Self-test

Run from the repository root:

```bash
node skills/design-system-ui/tests/run.mjs
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [assets/](assets/): Support files and templates.
- [examples/](examples/): Worked examples.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [ds.mjs](scripts/ds.mjs)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/design-system-ui` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
node scripts/ds.mjs detect /path/to/project
node scripts/ds.mjs audit /path/to/project --format md
node scripts/ds.mjs tokens /path/to/tokens.json --themes light,dark
```
