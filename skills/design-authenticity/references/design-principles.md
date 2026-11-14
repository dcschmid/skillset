# Design Principles — identity, layout, components, imagery

Purpose: the Design Identity Engine detail layer. Load when defining or reviewing
typography-adjacent structure, layout, components, or imagery. Typography families
and scales: `typography.md`. Color: `color-and-composition.md`.

## Prime frame

Every element answers one question: *why does this exist for THIS product?*
Information architecture before decoration. Density matched to task: an admin
table earns density; a portfolio earns breathing room. Neither is "the" style.

## Layout & composition

- **Hierarchy first.** One primary focus per screen region. Size/weight/position/
  contrast carry rank — color alone is not hierarchy.
- **Rhythm, not sameness.** Vary section rhythm deliberately: dense → sparse →
  dense reads editorial; uniform everywhere reads template. Change rhythm only
  where content demands it, and say where.
- **Whitespace is structure.** Deliberate gaps group and rank. No filler margins
  and no accidental crowding.
- **Grids serve content.** Column count, gutters, and breakpoints derive from
  content width and density needs, not from a framework default left untouched.
  Asymmetry is legal when it strengthens flow (editorial, creative) and never
  when it hides where to click.
- **Alignment and grouping** beat decoration for coherence. Proximity > dividers.

## Components — derive from function, not habit

Choose the component from the task + existing system. Rules that hold everywhere:

- **Cards** are for genuinely separate, parallel, referenceable units of content.
  Lists, tables, definition lists, prose sections, and tab groups are NOT cards by
  default. Card-in-card is a smell; nesting >1 deep needs justification.
- **Buttons**: primary action once per context; secondary/tertiary visibly
  subordinate; destructive visibly different. Labels are verbs + object
  ("Save layout", not "Submit").
- **Navigation**: depth and labels come from the user's task model. No identical
  mega-nav recycled across products. Breadcrumbs only where hierarchy is real.
- **Forms**: inline labels, visible focus, errors near field + announced
  (`accessibility` skill owns mechanics). Field order = task order.
- **Tables/dense data**: aligned numerics, row scanning comfort, sort/filter where
  the task needs it; do not tile a table into cards.
- **Status/notice**: semantic states (loading/empty/error/success) are designed
  states, not spinner + toast defaults. Empty states teach the next action.
- **Dataviz**: chart type from data shape and question; legend only when needed;
  color carries meaning, not vibes.

## Imagery & icons

- Project-relevant imagery beats stock/placeholder. Existing user-supplied assets
  and references outrank anything generated.
- Icons are functional signposts; a decorative icon row is noise. One icon style
  per project.
- Never invent customers, logos, testimonials, or product data. Missing content →
  real placeholder text marked TODO, not fabricated marketing.
- Illustration (when used) matches the chosen direction's line/weight/palette.

## Content voice (UI text is design)

Headings say what the thing IS ("Publish a build in 40 seconds"), not marketing
mist ("Unleash the future"). No fyllwords, no lorem in delivery. Text length
fits the layout; layout tolerates long real strings (i18n, names).

## Coherence test (reviewer's shortcut)

Squint: does the screen have ONE story (what matters) or MANY stories (equal
shouting)? Then check: could this screen belong to exactly ONE product (identity)
or would it pass for ten (generic)? Both must pass.
