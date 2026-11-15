# ultimate-testing-qa

Inspect existing tests, fill meaningful coverage gaps, and reproduce bugs in real browser flows. Follow issues through reproduction, repair, and retesting.

Profile: Private and Working. Preparation: Provide the URL or project path, start command, and critical user flow. Describe expected and actual results for bugs.

Expected result: A reproducible finding, an in-scope fix where applicable, relevant tests, and a record of checked and untested paths.

Requirements and limits: Existing runners and configuration take precedence. Playwright defaults to Firefox unless the project requires another browser. Automated checks do not establish overall product quality.

## ultimate-testing-qa: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh ultimate-testing-qa
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the ultimate-testing-qa skill. Double-clicking the form creates two orders. Reproduce the flow, fix the cause, and verify protection against duplicate submission.
```

**Codex:**

```text
Use the ultimate-testing-qa skill. Review existing login and checkout tests. Add the most important missing error paths within the current test setup.
```

**oh-my-pi:**

```text
Use the ultimate-testing-qa skill. Inspect the running site for console errors and failed requests. Test navigation and forms at narrow and wide viewports.
```

## ultimate-testing-qa: Self-test

Run from the repository root:

```bash
node skills/ultimate-testing-qa/tests/run.mjs
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

- [qa.mjs](scripts/qa.mjs)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/ultimate-testing-qa` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
node scripts/qa.mjs analyze /path/to/project --format md
```

## What the analyzer verifies

`qa.mjs analyze` inventories frameworks, runners, routes, and CI configuration.
It does not execute the target project's tests. Follow the inventory with the
project's own test commands and report which flows were actually exercised.
