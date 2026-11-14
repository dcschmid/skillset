# Anti-AI-Slop Detection Engine

Purpose: systematically detect generic, interchangeable, obviously-AI design
patterns in existing or new surfaces. Used by REVIEW, GUARD, and the CREATE gate.
Output = findings with schema below. Categories A–J.

## Finding schema (every finding)

| Field | Content |
|---|---|
| id | `A1`, `C3`, … |
| severity | `blocker` (a11y/broken) · `major` (identity-damaging, systemic) · `minor` (local, fixable) · `nit` (taste) |
| component | file/route/selector of the affected surface |
| observation | what is concretely visible (values, counts, selectors) |
| rationale | why it is a problem *for this product*, or "style decision" if not |
| fix | concrete change, inside existing system where one exists |
| before/after | optional, one line each |

## Classification filter (run before reporting)

A pattern is a finding ONLY when all hold:
1. It is **repeatable-template behavior** (would appear on an unrelated product).
2. It **hurts** this product's comprehension, identity, or task performance —
   or is unexplainable given the brief.
3. The fix fits the project's constraints.

Legitimate when: deliberate style choice fitting the direction (glassmorphism IS
the brand), project constraint (component library ships these radii), or taste
(reported as `nit` at most). **A well-built card is not a defect for being a
card. A gradient that is the brand is not slop.** No false-positive padding:
report few real findings over many marginal ones.

## Categories

### A. Generic color treatment
- Default indigo/violet→blue gradient (`from-indigo-500 to-blue-600`,
  `#6366f1`, `linear-gradient(...indigo/violet/blue...)`) as unexamined default.
- Same neutral ramp + one accent on every product regardless of domain.
- Heuristic: grep tokens/CSS for the tailwind-indigo/violet ranges and
  violet-blue `linear-gradient`s; if the product is not that brand → finding.
- Legal: brand IS violet; dark-first tool with one functional accent; editorial
  duotone. Check against brand source before reporting.

### B. Interchangeable typography
- Single family + one weight, size steps only `text-sm/base/lg/2xl/4xl/6xl`;
  no weight contrast; identical H1..H4 rhythm on every page type.
- Headings all `font-bold text-4xl` regardless of context; tracking/leading
  untouched (or `tracking-tight` everywhere).
- Test: does the typography differentiate a marketing page from a dashboard from
  an article? Same answers → generic. System fonts chosen consciously are legal;
  report only unchosen defaults. See `typography.md`.

### C. Repetitive layout structures
- Hero(centered H1 + subtitle + 2 CTAs) → 3–4 equal feature cards → CTA band →
  3-col footer, on every page and every product.
- Dashboard = N equal stat cards + 2 charts, independent of data.
- Equal-height card grids as default for non-parallel content.
- Heuristic: sibling sections with identical child counts/sizes/structure where
  content differs materially. Legal: parallel items genuinely ARE equal (pricing
  tiers); report only when content differs but layout says "same".

### D. Overdone visual effects
- Glass/blur, glow, shadow-lg/xl, rounded-2xl+, animated gradient borders without
  a functional or brand reason.
- Decoration stacks: backdrop-blur + gradient + big radius + shadow on one card.
- Heuristic: decorative-only props on container components; count blur/
  box-shadow/radius scale vs. state usage. Legal: glass IS the surface model
  (e.g., OS-chrome UI); big radius IS the brand (playful products).

### E. Missing brand identity
- Surface would survive a product-name swap unchanged (labels, headings, palette,
  copy all product-agnostic).
- Heuristic: swap test — rename the product; if nothing else must change, the
  design has no identity. Report with the first change that WOULD be product-
  specific (name typography, key color, section order).

### F. Unnecessary UI components
- Cards wrapping sections that are not parallel/referenceable units; card-in-card;
  icon grid where text links serve; tab bar for 2 items; modal for inline-able
  form.
- Test per component: remove it — does comprehension drop? No → finding `minor`.

### G. Unnatural content structure
- Marketing filler ("Unlock… Seamless… Empower"), lorem-style copy, invented
  testimonials/logos/metrics, headings describing layout not content.
- All text same length/structure (template rhythm). Legal: real client copy.

### H. Generic imagery
- Random decorative circles/blobs/emoji clusters; stock-looking illustrations
  unrelated to domain; icon sets mixed across styles; placeholder art shipped
  as final.
- Heuristic: absolute-positioned decorative shapes with no content role
  (`aria-hidden` blobs, `blur-3xl` circles) as page defaults.

### I. Missing visual hierarchy
- Everything equi-weighted (equal sizes/weights/contrast) OR many simultaneous
  focal points; primary action not findable in 2s; page reads flat at squint.
- Report with the re-rank proposal, not just the complaint.

### J. Inconsistent decisions
- Two radius scales on sibling components; multiple accent colors without state
  meaning; spacing scale drift (mixing 4/6/7 gaps or px values); heading scale
  drifts across routes; button variants multiply past their meanings.
- Legal: multiple accents ARE the data-viz encoding; separate apps in one repo
  may differ.

## Severity + score coupling

`blocker` findings cap the gate at "needs fixes" regardless of points
(`visual-quality-gates.md`). ≥2 `major` in one category usually means E (no
identity) — fix upstream, not per-symptom.

## False-positive discipline (binding)

- Reproduce the observation (selector/value/count) before reporting it.
- One finding per root cause; do not enumerate symptoms.
- If uncertain whether deliberate: read config/tokens/brand source; still
  unclear → classify `nit` with the question, never `major`.
- Never report a pattern because this file lists it — report it because THIS
  product's context says it does not belong.
