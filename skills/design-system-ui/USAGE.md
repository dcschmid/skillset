# Using the `design-system-ui` skill in your agents

Design-system and UI-component engineering for any web project (plus
game-UI token concepts for Godot/Defold). CREATE token systems (DTCG
v2025.10), AUDIT inconsistency (duplicate colors/buttons/spacing, broken
dark mode, unused tokens), FIX safely, MIGRATE legacy UI, VALIDATE
tokens/themes, DOCUMENT components. Boundaries: one-off styling is not a
system (just style it); deep a11y → accessibility; aesthetic originality →
design-authenticity; E2E/browser QA → ultimate-testing-qa.

## Install (this skill only)

```bash
tools/install-skills.sh design-system-ui
```

Symlinks into both host roots; remove with
`tools/uninstall-skills.sh design-system-ui`.

## Claude Code

Discovered from `~/.claude/skills/`; triggers on "design system", "design
tokens", "dark mode broken", "duplicate components":

```
Use the design-system-ui skill: audit this Astro project for duplicate
colors and spacing — file:line evidence, then the safe fix order.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the design-system-ui skill: CREATE a DTCG token system from our
Figma-exported palette; build step, no runtime dependency.
```

## oh-my-pi (omp)

omp routes from the skill list; `ds.mjs` is the deterministic lane:

```
Use the design-system-ui skill: MIGRATE the scattered hex values in
components/ onto tokens, VALIDATE both themes, keep diffs reviewable.
```

## Working style (all hosts)

- Evidence before edits; token builds run through the shipped pipeline.
- Direct automation:
  `node skills/design-system-ui/scripts/ds.mjs detect <project>`,
  `ds.mjs tokens|audit|report` (file:line evidence output).

## Examples that work verbatim

```
Use the design-system-ui skill: our dark mode breaks in three components
— audit, fix, and document the token contract that prevents regressions.
```

## Verify the skill itself

```bash
node skills/design-system-ui/tests/run.mjs
```

Exit 0 on PASS (zero-dep runner).
