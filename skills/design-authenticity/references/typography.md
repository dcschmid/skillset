# Typography — identity engine layer

Purpose: deliberate type selection per product. Load when choosing or reviewing
type. Never reflexively reuse the same family/scale across projects; system
stacks are valid when *chosen*. License/technical usability is part of the
decision.

## Selection procedure

1. Derive from product/audience/tone (from Discovery). A dev-tool ≠ music magazine
   ≠ game HUD ≠ corporate portal. Name the tone in 2 words first.
2. Pick a pairing that expresses it; state WHY in one line (traceable to product).
3. Verify usability: metric compatibility, weight availability, subset/licence,
   fallback stack, `font-display`, preload, self-host vs CDN.

## Family

- Body needs x-height/counter openness for its longest-running text; display may
  be characterful but must not fight legibility at its real sizes.
- Pair on contrast (serif/sans, humanist/geometric, wide/narrow) OR run one high-
  quality variable family with weight+width range. One or two families, rarely 3+.
- **Do not** ship the same default (system-ui / Inter / one geometric sans) on every
  project unless each project independently chose it. Reuse is fine; unchosen reuse
  is `B`-category slop (`anti-ai-patterns.md`).

## System-font legitimacy

`system-ui`/`-apple-system` stack is a deliberate choice for native-tool feel,
zero-weight cost, OS consistency — acceptable when stated. It is not a default to
escape the decision.

## Scale & hierarchy

- Modular ratio from density: dense UI 1.125–1.2 (small steps), editorial/landing
  1.25–1.5. Fixed px/rem or fluid `clamp()` with explicit min/max at real viewports.
- Ranks = f(content rank), not decoration. Distinct steps so rank survives a squint;
  adjacent steps must differ enough to read as rank, not as a rounding error.
- H1..H6 map to document structure, not size order; a page may skip sizes.

## Weights & opticals

- Weights carry meaning (body 400 / UI 500–600 / emphasis 700), not "everything
  bold". Tracking: tighten only large display; never tighten small body; letterspace
  small caps/labels slightly positive.
- Leading: body 1.5–1.75 (readability), display 1.0–1.2 (mass). Cap measure
  ~45–75ch; wide layouts need column width, not bigger font.

## Rhythm

- Vertical spacing on the spacing scale; line-length and block gaps create the
  rhythm; avoid uniform gaps that flatten sections (`design-principles.md`).
- Baseline-ish alignment between type and grid where it strengthens editorial feel;
  never at the cost of legibility or a11y line-height.

## Technical & legal usability (binding)

- Licences: confirm the family's licence permits the target use (web-embed,
  self-host, app bundle). Note licence in tokens/report.
- Subsetting: subset display faces; keep fallback metrics-matched (size-adjust).
- Performance: self-host or preload; `font-display: swap`/`optional` per need; count
  network requests.
- Scaling: type in `rem`/`clamp` so user zoom/text-scale holds (a11y, `accessibility`
  skill). No fixed-px body that clips on 200% zoom.
- Variable vs static: variable for range + few files; static where file count /
  engine support (game/Defold/Godot bitmap fonts) demands it.

## Per-context defaults (starting points, not templates — re-derive)

| Context | Body | Display | Scale | Notes |
|---|---|---|---|---|
| SaaS/dashboard | neutral grotesque, tabular numerals | often same family | 1.125–1.2 | density, scan speed |
| Editorial/magazine | high-legibility serif/sans | expressive display | 1.25–1.5 | measure, rhythm |
| Dev-tool/docs | mono for code + UI sans | minimal | tight | code/UI alignment |
| Game HUD/menu | engine-font constrained | themed | — | bitmap/SDF, no reflow |
| Portfolio/creative | chosen voice | bold, ownable | expressive | identity-first |

## Review checks (feeds REVIEW `B`)

Family chosen-with-reason? Ranks survive squint? Weights meaningful? Measure +
leading readable? Licence + delivery verified? Zoom/scale safe? Same answers across
unrelated products → report `B`.
