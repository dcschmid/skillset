# Theme Engine (light/dark/system/brands; game UI)

## Web strategy (binding)

One source: semantic tokens; a theme = a value-map over the semantic layer.
Mechanics per stack:
- CSS custom props: `:root{}` default(light) + `[data-theme="dark"]` /
  `.dark` overrides. class/data-attr beats media-query-only so user toggle
  + system both work.
- Tailwind: `darkMode:'class'` (v4: `@custom-variant dark`); tokens as
  `@theme`/CSS vars, NOT duplicated per breakpoint.
- CSS-in-JS: ThemeProvider with the same semantic keys; no second palette.

**No-flash SSR:** inline `<head>` script reading stored choice →
`document.documentElement.dataset.theme`, before first paint; server renders
light(default); framework-specific: astro = script tag in layout,
Next = `themeScript`/`next-themes` if project already has it.

Rules:
- Every theme covers **every semantic token** — `ds.mjs tokens --themes`
  theme-parity check is the gate (missing = P1).
- `prefers-color-scheme` only for *system* mode; `prefers-reduced-motion`
  gates every motion token (`duration-*` → 0ms or transform-free fallback).
- High-contrast = third theme over same names, not new names.
- Contrast per theme, both directions (dark bg/light text AND muted text):
  WCAG 2.2 AA 4.5:1 text / 3:1 UI — automated via accessibility skill's
  axe run on real pages; heuristics via ds.mjs `contrast-review`.
- System colors (`Canvas`/`CanvasText`) only inside system-theme contexts.
- Theme switch MUST be tested: toggle → screenshot parity + no unstyled flash.
  Multi-brand: brand = theme over shared semantics; layout tokens shared.

## Verification ladder
1. static: parity check (ds.mjs) · 2. rendered: axe contrast per theme
(accessibility skill) · 3. interaction: toggle test in component tests
(testing.md) · 4. build: SSR/SSG first-paint = final (no flash diff).

## Game UI (Godot 4.x / Defold) — principles port, mechanics differ

- **Port:** 3-tier token idea, naming discipline, contrast rules,
  state-coverage discipline (hover/active/focus equivalents).
- **Do NOT port:** CSS vars, prefers-color-scheme, web focus rings, DOM
  semantics, Storybook, viewport media queries.
- Tokens → engine-native theme: Godot `Theme` resource (ThemeTypes/
  ThemeItems, `theme_type_variation` for component tokens, default+dark
  theme pair). Defold: `.theme` GUI file per text/style/builder + runtime
  `gui.set_text`/color constants module mirroring the semantic layer.
- **Input:** gamepad/stick focus map (up/down/left/right + submit/back),
  never hover-dependent affordances; mouse/keyboard coexist (focus indicator
  on stick selection too). HUD/dialog state machine:
  `idle→open(pause?)→active→close` with explicit focus steal/return;
  modal dialog = input mode swap, not DOM overlay semantics.
- Reduced motion analog: engine "reduce motion" setting → shorten/kill
  tween tokens. i18n: UI must fit longest locale string (font + autosize).
- Test surface: engine headless (defold `defold-development`, godot
  headless-check) screenshots per theme, diff vs baseline — the web
  screenshot flow applies conceptually, harness is engine-side.
