# Keyboard & interaction audit

Tool: `node tooling/a11y-audit/bin/a11y.mjs keyboard --url <url>` (DOM focus
walk via Playwright). DOM evidence only — never reported as SR-tested.

## Automated checks (a11y keyboard)

1. forward Tab traversal: reaches every interactive element; loop completes
   (trap heuristic over `seen` map; MAX 60 tabs)
2. Shift+Tab: returns; landing on body = reported note
3. hidden-but-focusable and off-viewport stops (2.4.7/2.4.11 heuristic)
4. Escape: focus after close (dialog contract sample)
5. first in-page anchor as skip-link candidate (2.4.1 note)

## Manual keyboard protocol (auditor, per route)

- [ ] Tab from address bar: first stop = skip-link or first nav link
- [ ] every control reachable; focus ring visible at 400 % zoom
- [ ] Tab order = visual order (columns, grids, modals)
- [ ] Enter/Space activate buttons; arrows move in widgets (tabs, menus, tables)
- [ ] Home/End in widget stays inside widget; Esc closes without page scroll
- [ ] dialog: Tab cycles inside, restores focus to opener on close
- [ ] route change: focus moves to main heading or first content (SPA)
- [ ] drag alternative operable keyboard-only (2.5.7)
- [ ] no unexpected scroll/focus jump on input (3.2.2)

Record per-stop: sequence list — paste into report repro section.

## Component scenario templates (config steps)

```json
{ "name": "dialog-lifecycle", "steps": [
  { "click": "#open" }, { "expect": "#dlg-title" },
  { "press": "Tab" }, { "press": "Escape" },
  { "expect": "#open" } ] }
```
`a11y audit --config` runs these then axe-runs the open state — catches
violations invisible in initial DOM (proven: fixtures/dialog.html flow).

## ARIA state assertions (component tests, Vitest/Jest + jsdom or Playwright)

- after toggle: `aria-expanded` flips; roving tabindex exactly one `0`
- after submit: live region text equals success text; no duplicate announcements
- after error: input `aria-invalid=true` + describedby → message node exists

## Focus restoration (SPA)

After client route swap: heading or main container receives focus or
`role=status` announces new page; stale focusables from old page removed from
tab order (unmount or `inert`). Test: keyboard walk post-navigation equals
post-load walk (tooling: keyboard.ts second traversal).

## Evidence honesty

keyboard.ts prints `DOM evidence only, not a screenreader test` in gateNote —
preserve that distinction in every report. Real SR requires running SR
(screenreaders.md).
