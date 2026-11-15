# accessibility

Develop accessible interfaces and audit against WCAG 2.2. Combine automated axe checks with keyboard, focus, and screen reader evidence where the environment supports it.

Profile: Private and Working. Preparation: Specify routes, components, relevant states, and the target level. Include open dialogs and form error states in scope.

Expected result: Findings and fixes with separate results for automation, manual review, and screen reader testing.

Requirements and limits: A/AA form the binding baseline; AAA is a separate quality tier. Automated PASS does not establish full conformance. Screen reader automation requires a suitable environment; report missing prerequisites.

## accessibility: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh accessibility
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the accessibility skill. Audit /checkout for WCAG 2.2 AA. Check form errors, keyboard interaction, and focus. Separate automated findings from manual review items.
```

**Codex:**

```text
Use the accessibility skill. Fix the existing dialog so it receives sensible initial focus and returns focus when closed. Test Tab, Shift+Tab, and Escape.
```

**oh-my-pi:**

```text
Use the accessibility skill. Check save-status announcements with a screen reader if the environment allows it. Record missing evidence instead of reporting a blanket PASS.
```

## accessibility: Self-test

Run from the repository root:

```bash
python3 skills/accessibility/tests/test_skill.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [examples/](examples/): Worked examples.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [check-standards.mjs](scripts/check-standards.mjs)
- [setup-check.sh](scripts/setup-check.sh)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/accessibility` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
bash scripts/setup-check.sh
node tooling/a11y-audit/bin/a11y.mjs check
node tooling/a11y-audit/bin/a11y.mjs audit --url http://localhost:4321 --level aa
```
