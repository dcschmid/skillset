# design-authenticity

Create or review a visual identity based on the product, audience, and use. Assess typography, color, layout, and generic patterns against actual interfaces.

Profile: Private. Preparation: Provide the product context, audience, existing brand, and surface. Visual reviews require screenshots or browser access.

Expected result: A reasoned design direction, evidence-backed visual review, or revision with before-and-after comparison.

Requirements and limits: WCAG AA is the floor. Scores require visual review; otherwise report VISUAL_REVIEW_REQUIRED. Existing brand and design requirements remain binding.

## design-authenticity: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh design-authenticity
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude private
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the design-authenticity skill. REVIEW the existing home page. Identify generic patterns and justify changes using our product context and existing brand.
```

**Codex:**

```text
Use the design-authenticity skill. CREATE a visual direction for a research tool. Explain typography, density, and color choices for long reading sessions.
```

**oh-my-pi:**

```text
Use the design-authenticity skill. Use GUARD mode to check the new component against our identity rules. Compare its screenshot with existing screens.
```

## design-authenticity: Self-test

Run from the repository root:

```bash
python3 skills/design-authenticity/tests/test_skill.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [workflows/](workflows/): Task-specific procedures.
- [examples/](examples/): Worked examples.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [screenshot_audit.sh](scripts/screenshot_audit.sh)
- [validate_config.mjs](scripts/validate_config.mjs)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/design-authenticity` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
node scripts/validate_config.mjs /path/to/identity-config.yaml
```
