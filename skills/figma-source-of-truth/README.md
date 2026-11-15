# figma-source-of-truth

Keep the Figma design system, variables, and Code Connect mappings authoritative during UI implementation. Reuse production components and report concrete deviations.

Profile: Working. Preparation: Provide the Figma file and node, relevant library, and existing Code Connect mappings.

Expected result: An implementation using existing components and tokens, or an evidence-backed mismatch report naming the relevant nodes.

Requirements and limits: This Working-profile skill applies only when Figma is involved. It does not provide a Figma connection. Required plugin tools and their own prerequisites must be available.

## figma-source-of-truth: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh figma-source-of-truth
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude working
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the figma-source-of-truth skill. Implement the checkout view from the supplied Figma node. Use existing Code Connect components and library variables.
```

**Codex:**

```text
Use the figma-source-of-truth skill. Compare our button with the supplied library node. Report mismatched states, dimensions, and tokens without introducing a new design.
```

**oh-my-pi:**

```text
Use the figma-source-of-truth skill. Before implementation, check which components already have mappings. Identify missing mappings and unresolved design decisions.
```

## figma-source-of-truth: Self-test

Run from the repository root:

```bash
python3 skills/figma-source-of-truth/tests/test_skill.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [tests/](tests/): Self-tests and fixtures.
