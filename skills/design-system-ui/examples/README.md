# Design-system examples: inconsistent and cleaned up

The fixtures form a before-and-after pair for the auditor. `fixture-messy/`
contains deliberate duplicate components, repeated colors, inconsistent spacing,
and problematic focus rules. Its token source is valid. `fixture-clean/` shows
the target state with tokens, component states, visible focus, and reduced-motion
support.

Run from the repository root:

```bash
node skills/design-system-ui/scripts/ds.mjs audit skills/design-system-ui/examples/fixture-messy --format md
node skills/design-system-ui/scripts/ds.mjs audit skills/design-system-ui/examples/fixture-clean --format md
node skills/design-system-ui/tests/run.mjs
```

Findings in the messy fixture are expected. Do not clean it up: tests depend on
the auditor detecting its flaws. The clean fixture's `tokens.css` is marked as
a generated file.

For your own project, ask:

```text
Use design-system-ui. Audit our src/ using the before-and-after examples as
a reference. Report mismatches first and plan the migration in small steps.
```

See the [skill README](../README.md) for installation and more examples.
