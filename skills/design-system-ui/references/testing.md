# Testing & quality gates (design-system scope)

Division: this skill = token/component/theme tests. Browser harness,
E2E flows → ultimate-testing-qa. a11y engine (axe/SR) → accessibility skill.
Project's existing runners win (vitest/jest/playwright/storybook-test);
none present → the smallest runner that runs, zero new deps otherwise
(node:test is the floor).

## Token tests (ds.mjs IS the test — CI-ready)
```bash
node scripts/ds.mjs tokens tokens/*.json --themes light,dark   # exit 1 on P0
```
covers: DTCG shape · missing/cyclic aliases · type mismatch · theme parity ·
dup values. Add regen gate: `build && git diff --exit-code generated/`.

## Component tests (per shipped component, project runner)
render matrix (variant×size×state) · prop/event contracts · state machine
(open/close/focus restore) · keyboard (Tab/Enter/Esc/arrows per APG pattern)
· error+loading paths · a11y attrs (roles/labels via project's dom utils —
jsdom ok; REAL announcements = accessibility skill harness).
Controlled+uncontrolled both if API offers both. SSR: renderToString smoke.

## Visual regression (Playwright screenshot per component/route)
Baseline = reviewed screenshots, committed, human-approved once.
Matrix: variants×states × {light,dark} × {mobile,desktop} × long-text locale.
Flow: capture → diff vs baseline → FAIL on diff → human reads diff →
approve (re-commit baseline) or fix. Auto-accept-after-screenshot forbidden
(brief §15). Token-change runs = same flow, diff = the review doc.

## Theme tests
parity check (above) + toggle test: set light/dark → contrast assertions +
screenshot pair. SSR: served HTML (no JS) = final first-paint theme (flash check).

## Quality gates (release blockers)
tokens P0=0 · theme parity complete · component tests green · visual diffs
reviewed · contrast AA per theme (axe run or manual protocol) · a11y:
P0=0 (keyboard walk + axe on touched routes). Each gate prints PASS/FAIL/
NOT-TESTED+reason; NOT-TESTED never counts as PASS.

## Storybook (when project has it)
Story per state listed in component-architecture §docs;
`@storybook/addon-a11y` (axe panel) + interaction tests (play function or
`storybook/test`) for keyboard flows. If stack can't host a Storybook
version, docs live as example pages/md — never force incompatible deps.

## Game UI
engine-side: Godot GUT/`--headless` smoke + theme screenshot per theme;
Defold `defold --headless` + `gui` capture via defold-development runners.
Web runners don't apply; principles (baseline+review, state matrix) do.
