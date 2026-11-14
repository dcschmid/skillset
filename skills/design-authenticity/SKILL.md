---
name: design-authenticity
description: >
  Universal design authenticity and anti-AI-slop discipline for any UI surface (websites,
  SaaS, dashboards, docs, PWA, game menus/HUDs; audits existing React/Next/Astro projects
  too). Use when designing or building UI, redesigning interfaces, authoring design systems,
  defining visual identity (typography, color, layout), or reviewing designs for generic
  AI-generated patterns (default gradients, hero+card layouts, glass/glow blobs, template
  typography, decoration without purpose). Modes: CREATE, REVIEW, REFACTOR, GUARD. Enforces
  product-context-first design, a Design Identity Engine, Anti-AI-Slop detection, a
  100-point visual gate (target >=90), screenshot review when a browser exists, WCAG AA as
  hard floor. Framework skills own architecture; accessibility owns a11y engineering; this
  skill owns visual originality, coherence, product-fit. Existing projects: zero-code
  audits, prioritized audit-and-fix, brand-preserving modernization, before/after regression
  review. Zero external services.
---

# Design Authenticity (universal)

Every design decision is **justified and product-fit**, never a recycled recipe.
This skill stops unexamined, interchangeable, obviously-AI output. It does NOT
ban gradients, cards, glass, shadows, or any specific look — those are legal when
they earn their place. Read the mode, run the discovery proportional to scope,
then gate the result.

## Prime Directive

1. **Product context before pixels.** Never ship a design chosen only from a
   generic template. If a decision cannot be traced to the product, audience,
   task, or brand, it is decoration — justify or drop it.
2. **Originality preserves usability.** Distinctive, not confusing. Do not break
   UX conventions the user needs to operate the product. Accessibility (WCAG AA)
   and working interaction are hard floors a "look" never overrides.
3. **Existing brand/system wins.** In a project with tokens/components, improve
   *within* the system by default. Touch base tokens only with a stated reason.
   Small task → no surprise full redesign.
4. **Evidence over assertion.** Judge from the rendered surface when a browser
   exists; from source only when it does not. Never claim a review/screenshot you
   did not perform.

## Mode gate (pick the spine first)

Greenfield / authoring:

| Mode | Trigger | Spine | Detail |
|---|---|---|---|
| **CREATE** | new UI/page/design system | discovery → direction → system → build → render → authenticity → refine → gate | `workflows/create.md` |
| **REVIEW** | audit existing design, "check/review", no code change | capture → detect → classify → report | `workflows/review.md` |
| **REFACTOR** | improve existing design, keep behavior | preserve inventory → targeted improve → regression check | `workflows/refactor.md` |
| **GUARD** | inline during UI coding, catch slop early | cheap pattern scan → fix-in-place → proceed | `workflows/guard.md` |

Existing projects (auto project-discovery first — `references/project-discovery.md`;
selective scope stays scope; report `references/audit-report-format.md`):

| Mode | Trigger | Spine | Detail |
|---|---|---|---|
| **AUDIT** | full/selective analysis, ZERO code changes | discovery → render → A–H categories → consistency → score | `workflows/existing-project-audit.md` |
| **AUDIT_AND_FIX** | analyze + fix, prioritized P0–P3 | baseline → diagnose → plan → safe fixes → verify → re-audit | `workflows/audit-and-fix.md` |
| **DESIGN_MODERNIZATION** | modernize without killing brand | identity lock → evolve-in-system → anti-template guard → preservation regression | `workflows/design-modernization.md` |
| **ANTI_AI_SLOP_CLEANUP** | targeted generic-pattern sweep | detect A–J → context-filter → safe-remove → verify | `workflows/anti-ai-slop-cleanup.md` |
| **VISUAL_REGRESSION_REVIEW** | did changes break surfaces? | change inventory → parity capture → classify diffs → repair | `workflows/visual-regression-review.md` |

GUARD auto-engages on relevant UI tasks (new/edited UI code, styling, layout) and
stays light — it never blocks a whole step for trivia. It does NOT fire on backend,
pure-logic, or non-visual refactors. AUDIT never becomes a fix without a fix task
(`references/safe-auto-fix.md`).

## Discovery (proportional, before CREATE / REFACTOR)

Read the project first — never ask what the project already answers. Extract:

1. Product & audience & core tasks. 2. Existing brand/identity.
3. Existing tokens/components/`references`. 4. Binding design constraints.
5. Design problems to solve. 6. Tech constraints. 7. A11y needs.
8. What must be preserved.

Sources: source files, design tokens/CSS, components, docs, screenshots, any
`profiles/<project>.md` overlay named by the invocation. Simple change → 1-2
sentence internal discovery. Large/greenfield → full pass; if direction is
ambiguous, draft **2-3 distinct** directions and pick the most defensible (state why).

## Design Identity Engine (CREATE)

Define, per product — do not reuse a house style. Details in `references/`:

- **Typography** (`references/typography.md`): family, hierarchy, weights, scale,
  leading, rhythm, license/technical usability. No reflexive same-font default.
  System fonts are valid when *chosen*.
- **Color & composition** (`references/color-and-composition.md`): brand/functional/
  semantic/neutrals, contrast, light+dark, contextual color psychology. No
  auto purple-blue.
- **Layout & composition**: hierarchy, varied rhythm, deliberate whitespace,
  meaningful grid, density, asymmetry/editorial when fitting, alignment, emphasis.
  Never usability-for-novelty.
- **Components** (`references/design-principles.md`): derive from function + system,
  not card-by-default. Buttons/nav/cards/forms/tables/dialogs/tabs/search/dataviz/
  status/notices.
- **Imagery/icons**: project-relevant; consistent; purposeful icons; no placeholder
  illustrations as a fake "done"; no invented logos/testimonials/product data.
- **Directions** (`references/design-directions.md`): editorial/minimal/brutalist/
  swiss/retro/industrial/futurist/corporate/playful/typographic/dense/premium/
  experimental/gaming/pixel/musical/technical/organic — inspiration, not templates.

## Anti-AI-Slop Detection Engine (REVIEW / GUARD / gate in CREATE / AUDIT modes)

Systematic scan of existing and new surfaces. Categories A-J and finding schema
(finding → severity → component → observation → rationale → fix → optional
before/after) in `references/anti-ai-patterns.md`.

**Classify every finding** as real design problem / deliberate style choice /
project constraint / taste. Report **no false positives**: a well-built card is
not a defect for being a card. Severity + component + concrete observation +
rationale + fix.

## Visual Quality Gate (100 pts, target >=90)

Weighted rubric — independent identity 20 · typography/hierarchy 15 · layout/
composition 15 · product/audience-fit 15 · components/consistency 10 · content
credibility 10 · responsive 5 · accessibility 10. Rubric and scoring rules in
`references/visual-quality-gates.md`. A high score never hides a blocker:
a11y blockers, broken interaction, or real responsive failures MUST be fixed
regardless of score. Cite concrete observations; without a real render emit
`VISUAL_REVIEW_REQUIRED`, never a fabricated number. Existing-project modes add
a before/after column pair (`visual-regression.md` + audit report); numbers are
real observations or withheld, never invented.

## Rendering / screenshot review (optional, browser-gated)

Prefer repo tooling. Playwright + axe live under the `accessibility` skill's
`tooling/a11y-audit`; use `scripts/screenshot_audit.sh` to drive an available
browser for viewports (mobile/tablet/desktop/large) × light/dark × hover/focus/
menus/dialogs/form-errors/loading/empty/long-text/responsive-nav. **No browser →
screenshot checks are NOT reported as passed.** Source-only inference is stated as
such. Diff ≠ quality verdict. Before/after parity + diff classification:
`references/visual-regression.md`. `references/visual-quality-gates.md` § tooling.

## Accessibility floor

WCAG 2.2 AA minimum (AAA where realistic) via the `accessibility` skill;
`references/accessibility-integration.md`. Originality never excuses a barrier.
This skill owns visual originality/coherence; a11y engineering stays with the
accessibility skill — do not duplicate its rules.

## Framework & skill integration

Framework skills (`astro`, `react-nextjs`, `godot`, `defold-development`) own
technical architecture + best practices; `accessibility` owns a11y; **this skill**
owns visual quality, originality, coherence. On conflict: explicit project
requirements + functional/a11y-operable UX win. `references/framework-integration.md`.
Independent: no cross-skill import required; integration is opportunistic reuse of
existing tooling, never a dependency.

## Existing-project discipline (AUDIT modes)

Auto-discover before touching anything (`references/project-discovery.md`);
selective scope from the request stays the scope. Fixes follow
`references/safe-auto-fix.md`: minimal, reversible, token/component-first, no
dependency creep, uncommitted work never overwritten, audit never silently
becomes refactor. Cross-page consistency checked, deliberately different page
types kept different (`anti-ai-patterns.md` J). Content facts/prices/legal copy
read-only unless tasked; editorial rewrite → Human-Writing capability when the
project's skill set has one. CI fit: report + advisory findings by default;
subjective design scores NEVER block builds — only blocker-class a11y/broken
interaction gates, and only where the project's CI already gates. Report via
`references/audit-report-format.md`.

## Binding rules for coding agents

1. No design from a generic template alone. 2. Product context before styling.
3. Respect existing brand identity. 4. No arbitrary decorative effects.
5. No reflexive repeat of typical AI layouts. 6. Choose typography deliberately.
7. Information architecture before decoration. 8. Derive components from real need.
9. Handle responsive. 10. Never trade a11y for effects. 11. Review the render when a
browser exists. 12. Detect generic patterns, improve with rationale. 13. Preserve
working features. 14. No unnecessary dependencies. 15. No false claims about checks
performed. + Originality never destroys helpful UX conventions.

## Configuration (optional, never required)

Defaults are sane; a config sharpens them. `examples/design-config.example.yaml`
(authoring) and `examples/existing-project-config.example.yaml` (mode, selective
scope, project tools, preservation list, risk ceiling, fix priorities, report
path) document direction, brand colors, typography, existing design system,
anti-pattern strictness, minimum quality, allowed effects, preferred components,
screenshot testing, max refine iterations, a11y target, project notes. Absent
config → sensible defaults. Load a `profiles/<project>.md` overlay only when the
invocation names it.

## Files

`references/`: `design-principles.md` · `anti-ai-patterns.md` · `typography.md` ·
`color-and-composition.md` · `design-directions.md` · `accessibility-integration.md`
· `visual-quality-gates.md` · `framework-integration.md` · `project-discovery.md` ·
`safe-auto-fix.md` · `visual-regression.md` · `audit-report-format.md`.
`workflows/`: `create.md` · `review.md` · `refactor.md` · `guard.md` ·
`existing-project-audit.md` · `audit-and-fix.md` · `design-modernization.md` ·
`anti-ai-slop-cleanup.md` · `visual-regression-review.md`.
`examples/`: `design-config.example.yaml` · `design-review.example.md` ·
`existing-project-config.example.yaml` · `existing-project-audit.example.md`.
`scripts/`: `screenshot_audit.sh` (browser-gated), `validate_config.mjs` (opt-in).
Validation: `python3 tests/test_skill.py` → VERDICT.

## Iterate bound

Cap auto-refine loops at the configured maximum (default 2). On cap, deliver best +
list open issues. Never loop forever.
