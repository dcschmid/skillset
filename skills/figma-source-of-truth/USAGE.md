# Using the `figma-source-of-truth` skill in your agents

Figma-as-source-of-truth UI policy for projects that have a Figma design
system: Figma and Code Connect decisions outrank general frontend guidance;
implementation must not invent a competing design system. inert without
Figma — `design-authenticity` and `design-system-ui` stay in charge there.

## Install (this skill only)

```bash
tools/install-skills.sh figma-source-of-truth
```

## Invoke

```text
Use the figma-source-of-truth skill: build the checkout component against
Figma node 12:340; Code Connect maps it to <CheckoutSummary>.
```

```text
Use the figma-source-of-truth skill: our button diverges from the library —
report the mismatch against the named nodes, do not redesign.
```

## Verify

```bash
python3 skills/figma-source-of-truth/tests/test_skill.py
```
