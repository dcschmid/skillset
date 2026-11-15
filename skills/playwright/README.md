# playwright

Use existing terminal browser tools to open pages, inspect states, reproduce interactions, and capture screenshots or traces.

Profile: Private and Working. Preparation: Provide the URL, start command, flow, and expected result. Use the intended secure context for test credentials.

Expected result: A reproducible flow with observed states, browser errors, and useful artifacts.

Requirements and limits: Firefox is the default unless the repository requires another browser. Prefer existing project tools; do not install a second global CLI just because the skill is present. Use element references from a fresh snapshot.

## playwright: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh playwright
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the playwright skill. Open http://localhost:4321 in Firefox and check the mobile menu. Record opening, navigation, and closing using fresh snapshots.
```

**Codex:**

```text
Use the playwright skill. Reproduce the search-dialog bug: after Escape, it cannot be reopened. Check browser errors and capture a trace if needed.
```

**oh-my-pi:**

```text
Use the playwright skill. Check the local login flow with the designated test data. Use a separate project session and record the result.
```

## playwright: Self-test

Run from the repository root:

```bash
python3 skills/playwright/tests/test_skill.py
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

- [playwright_cli.sh](scripts/playwright_cli.sh)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/playwright` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
bash scripts/playwright_cli.sh --help
```

## Resolve an existing browser CLI

The wrapper checks `PLAYWRIGHT_CLI`, then `playwright-cli`, then `mm-playwright`.
It installs nothing. Follow the resolved tool's help to select Firefox unless
the project specifies another browser. Open the local URL and read a fresh
snapshot before using an element reference. See [the CLI reference](references/cli.md)
and [workflow examples](references/workflows.md) for details.
