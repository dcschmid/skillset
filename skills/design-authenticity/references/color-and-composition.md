# Color & Composition — identity engine layer

Purpose: product-derived color systems and compositional structure. No automatic
palette; every ramp traces to brand, function, or semantics.

## Color system procedure

1. Source of truth: brand asset, existing tokens, content imagery, or a stated
   direction. No source → propose one WITH rationale and mark it a proposal.
2. Build tiers (name by role, never by hue-in-the-abstract):
   - **brand**: primary + tints for hover/active/disabled; usage share decided
     per product (a tool may be 95% neutral; a poster 40% brand).
   - **neutrals**: bg/surface/border/text ramp with intentional temperature
     (warm/cool), not raw gray; dark+light both designed, not auto-inverted.
   - **functional/semantic**: success/warning/error/info/link each with a reason;
     hue chosen for discrimination, checked by contrast math, not habit.
   - **accent**: rare, for the ONE action/insight that must win.
3. Contrast: text/interactive ≥ the accessibility floor (delegates to
   `accessibility-integration.md`); compute, don't eyeball.
4. Dark/light: author both; a palette that only works on one background is half
   a system. Same hue intent, rebalanced lightness/chroma — not a mechanical flip.

## Anti-default checks (feeds REVIEW `A`)

- Violet/indigo→blue gradient as primary: default or brand? (Check brand source.)
- One accent doing four jobs (link + primary + success + focus) → split by meaning.
- Pure black/white text on tinted bg (harsh) vs designed ink/paper values.
- Color carrying meaning with no non-color backup (→ a11y, but also clarity).

## Color psychology is contextual

Red = error in a tool, appetite in food, premium in wine. Never apply a universal
"blue = trust" lookup; ask what THIS audience reads first.

## Composition beyond color

- **Density dial**: match information-per-viewport to task (dashboards high,
  onboarding low). Density is a design output, not a framework default.
- **Emphasis budget**: per screen, one primary + a capped number of secondary
  signals; every extra highlight demotes all others.
- **Surface model**: elevation/depth (shadow tiers, borders, or flat planes) must
  match the platform and direction; a single shadow language, tokens-named.
  `shadow-lg/xl` as decoration → `D`; shadow encoding real z-order → fine.
- **Radius/scale language**: one family of radii and steps tied to component size
  and direction. `rounded-2xl` everywhere is a choice only some directions made.
- **Grids**: columns/gutters from content; span asymmetry for rhythm where the
  direction allows (`design-principles.md` rules stay binding).

## Tokens (implementation bridge)

Express the system as tokens (CSS custom properties, theme object, or the
project's existing token file) with roles, not one-off literals; components
consume tokens. Editing existing token VALUES needs a reason; adding roles is
preferred over replacing (framework + preservation rules).
