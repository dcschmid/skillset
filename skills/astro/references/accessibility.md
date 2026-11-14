# Accessibility — WCAG 2.2 AA as build default

A11y is authored in, not tested in. AA is the target; automation (axe) catches
a fraction — manual passes cover the rest.

## Authored-in requirements

- **Semantics**: one `h1`, ordered headings; landmarks (`header/nav/main/
  footer`, `nav` labelled when multiple); lists for list content; `table` with
  `th scope`; `<time datetime>` for dates.
- **Images**: `alt` on every `<img>` (`""` decorative); `aria-hidden` on purely
  decorative inline SVG; no `alt` in captions duplicated.
- **Forms**: every control has a programmatic `<label for>`/wrapped label;
  errors reference the control (`aria-describedby`), text + color; native
  validation or Actions messages human-readable.
- **Keyboard**: all interactions reachable and operable; visible `:focus-visible`
  styles (token: `--focus-ring`, ≥3:1 against adjacent); logical tab order, no
  positive `tabindex` traps.
- **Dialogs/menus**: `dialog`+`showModal` (native focus trap + Esc) or
  documented equivalent; focus returns to invoker.
- **Contrast**: token pairs ≥4.5:1 body, ≥3:1 large/UI; check token pairs once
  per theme (light+dark), not per component.
- **Text scaling**: rem-based tokens, layouts survive 200% zoom (wrap/reflow,
  no fixed-px heights on text boxes).
- **Reduced motion**: every animation in `prefers-reduced-motion` guard.
- **Live regions**: only for genuinely async updates (`aria-live="polite"` on
  search results count); no announcements for decoration.

## Astro-specific notes

- Scoped styles don't affect a11y; ensure global focus-visible lives in
  `global.css` so every route has it.
- `client:visible` islands: skeleton with final size → no CLS + no focus jump;
  content present in DOM pre-hydration when server-rendered (SSR) — prefer.
- Forms via Actions: server-rendered error state keeps screen-reader order
  stable (no JS announcement timing issues).
- `astro:transitions` ClientRouter: announce route change minimally or accept
  default (focus to `main`); skip-link target `id="main"` exists.

## Verification ladder

- AUTOMATED: axe-core via `@axe-core/playwright` in Playwright lane
  (testing.md) — run on 3 representative templates (home, content, dynamic).
- MANUAL (record pass/fail): keyboard-only tour; zoom 200%; screen-reader
  smoke (one SR); reduced-motion emulation; contrast spot-check on token pairs.
- Report format: "axe N violations (list) + manual checks: pass/fail per
  check" — never "fully accessible".
