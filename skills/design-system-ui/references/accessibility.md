# Accessibility (design-system layer; depth → accessibility skill)

Floor: WCAG 2.2 AA (Rec 2024-12-12); AAA where cheap (large text contrast,
focus appearance). The `accessibility` skill owns audits, axe/SR harness,
WCAG verdicts — this file = what a component/token/theme must do so the
audit passes later.

## Component a11y checklist (ship-blockers)
- **Name:** every control has accessible name (label element, aria-label
  only when no visible text possible; Icon-only Button → label + tooltip).
- **Semantics:** native element first (button/a/input/dialog); ARIA role
  only when no native equivalent (APG pattern for the widget chosen).
- **Keyboard:** all interactive reachable+operable (Tab order = DOM order;
  overlay: trap→Esc closes→focus returns to opener; menus: arrows per APG).
- **Focus visible:** token `focus-indicator` every interactive state;
  `outline:none` forbidden without same-rule replacement.
- **States announced:** disabled→aria-disabled or native disabled; loading→
  `aria-busy`+live region for completion; error→`aria-describedby` message +
  `aria-invalid`; status toasts → `role=status`/`aria-live=polite`.
- **Forms:** Input always label-bound (`for`/wrapping); ValidationMessage
  linked; Fieldset/legend for groups; Switch/Checkbox keep native input.
- **Overlay:** `<dialog>`/`showModal()` or primitive with same guarantees
  (inert background, scroll lock w/o layout shift, restore focus).
- **Targets:** ≥24×24 (2.5.8), spacing between ≥ 8 for touch density.
- **Motion:** reduced-motion fallback for every animated component (tokens).
- **Zoom/reflow:** text scales 400% without loss (1.4.4/1.4.10), no fixed
  px heights on content; no horizontal scroll at 320px.

## Token-layer a11y
- every theme's `text-*` on its `background-*` ≥ 4.5:1 (small) / 3:1 (large);
  `border-strong`+`focus-indicator` ≥ 3:1 vs adjacent (1.4.11 non-text);
  status colors never sole-meaning (icon/text paired — 1.4.1).
- ds.mjs `contrast-review` = heuristic pre-flag; the PASS claim comes only
  from axe (browser) or measured values, by accessibility skill.

## Test hooks (per testing.md)
keyboard walks + axe-core run + manual SR spot (names, announcements,
dialog behavior) — automated PASS never equals conformance claim; report
always splits automated / manual / SR evidence.
