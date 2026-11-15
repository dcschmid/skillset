---
name: figma-source-of-truth
description: >
  Figma-as-source-of-truth UI policy for projects that have a Figma design
  system: Figma and Code Connect decisions outrank general frontend guidance
  and implementation must not invent a competing design system. Use when
  building or reviewing UI in a project with Figma designs or Code Connect:
  colors, spacing scales, typography, variants, component APIs, interaction
  patterns. Projects without Figma keep normal design skills in charge.
---

# Figma is the source of truth

For UI tasks in projects that have a Figma design system, Figma is the visual
and interaction source of truth. Use Code Connect and existing production
components when available. Do not invent colors, spacing scales, typography,
variants, component APIs, or interaction patterns when the design system
already defines them.

General frontend guidance (framework skills, design skills, accessibility)
may improve implementation quality, performance, accessibility, and code
structure, but it must not override an explicit Figma or Code Connect
decision. If implementation and design disagree, surface the mismatch
instead of silently redesigning the interface.

## Scope gate

This policy binds only where Figma is the authority. Establish that first:

- Project documents Figma as design source, or a Figma file key / Code Connect
  mapping exists in the repo.
- No: this skill stays inert; `design-authenticity` and `design-system-ui`
  own the design work.

## Working rules

1. Before implementing a component, resolve it to a Figma node or Code
   Connect component; cite which one backs tokens, variants, and API.
2. Tokens (color, spacing, type) come from the Figma library or its exported
   code. No local one-off values where a token exists.
3. Production components win: reuse or extend existing components instead of
   proposing parallel ones.
4. Improve freely within the decided surface: structure, performance,
   accessibility, states the design did not specify (loading, error, empty).
5. Divergence is a report, not a redesign: state where code and design
   disagree, which side should change, and let the design owner decide.

## Evidence

- **Read:** Figma files/exports, Code Connect config, existing component
  code.
- **Report:** token or component mismatches with node names and file paths.
- **Never:** invent a competing scale, or quietly replace a specified
  interaction.
