# figma-source-of-truth

Figma-as-source-of-truth UI policy: in projects that have a Figma design
system, Figma and Code Connect decisions outrank general frontend guidance,
and implementation must not invent a competing design system. Token sources,
component reuse, and divergence reporting only — design authoring stays with
`design-authenticity`, token systems with `design-system-ui`, a11y with
`accessibility`. Inert in projects without Figma.

## Quickstart

```bash
tools/install-skills.sh figma-source-of-truth
```

```text
Use the figma-source-of-truth skill: build the checkout component against
Figma node 12:340; report mismatches, do not redesign.
```

Verify: `python3 skills/figma-source-of-truth/tests/test_skill.py`
