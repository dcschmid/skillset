# Component Architecture (bar + catalog + i18n/responsive)

## Per-component contract (binding when you ship it)

1. **API:** typed props (TS types/prop-types per project lang); explicit
   public surface, internal helpers not exported. Sensible defaults;
   variants = enum prop (`variant:'primary'|'ghost'…`), sizes enum
   (`sm|md|lg`), documented in the component doc (assets/ templates).
2. **States — full grid or documented subset:** default, hover, active,
   focus-visible (NEVER `outline:none` without replacement), disabled
   (no pointer-events + aria-disabled parity), loading (spinner keeps size —
   no layout shift), error, empty. Interactive = controlled AND
   uncontrolled (`value`/`defaultValue` + `onValueChange`) when the project
   pattern allows; pick project's existing pattern first.
3. **Semantics ladder:** native element → native+ARIA gap → framework
   primitive (Radix/React Aria/headless) → custom (last resort; full
   keyboard+ARIA on you). Dialog/Select/Menu/Tooltip: reuse, don't reinvent
   (`<dialog>`+`.showModal()` fine for simple, project primitive otherwise).
4. **A11y floor (deeper: accessibility skill):** accessible name
   (label/aria-label content), roles only when element lacks them, focus
   management in overlays (trap in, restore out, Esc), live regions for
   async status, keyboard per WAI-ARIA APG pattern of chosen widget.
5. **Engineering:** no listener leaks (cleanup in effect/`onDestroy`),
   no rerender storms (stable props, memo only measured), SSR-safe
   (no window/document at module/render top level; guarded in effect),
   refs forwarded when project's consumers need DOM (React.forwardRef /
   `ref` prop in React 19 / `bind:this`+expose in Svelte/Vue defineExpose).
6. **Performance:** leaf modules (tree-shakeable: one component per file,
   barrel exports minimal), icon lib imported once (project's chosen set),
   font loading via project strategy, animations only transform/opacity
   tokens, CSS bundle grows only with used styles (tailwind JIT ok).

## Catalog = menu, not mandate

Foundation: Button IconButton Link Typography Icon Badge Divider Container
Stack Grid Surface · Form: Input Textarea Select Checkbox RadioGroup Switch
Slider Field Fieldset ValidationMessage · Feedback: Alert Toast Tooltip
Progress Spinner Skeleton EmptyState ErrorState · Nav: Tabs Breadcrumbs
Pagination DropdownMenu Sidebar NavMenu Stepper · Overlay: Dialog
AlertDialog Drawer Popover ContextMenu · Data: Table DataTable Card
Accordion List Avatar Stat ChartContainer.
Build only what a page uses (or uses twice). No component "complete sets".

## Component identity discipline

New component copies PROJECT conventions: dir layout (`ui/` vs
`components/`), styling (tailwind classes vs css file vs css-in-js), prop
naming (`class` vs `className` passthrough, `asChild` vs render prop),
export style. Existing Button wins over your ideal Button. Two similar
existing buttons → merge to one API behind a codemod + keep-thin-re-export
only during migration window (references/migration.md).

## i18n + responsive (every component)

- Longest-locale-safe: no fixed widths on text hosts; `min-w-0` in flex,
  wrapping or truncation w/ title; German compound words survive (no
  break-all unless column). Numbers/dates via project formatter, not
  hardcoded.
- RTL: logical properties (`margin-inline-start`, `padding-inline`,
  `inset-inline`, `text-align:start`); directional transforms mirrored via
  `[dir=rtl]` or `ltr:/rtl:` variants; icons that indicate direction flip.
- Zoom: 200% text reflows (no fixed px heights on text blocks), touch
  targets ≥24×24 CSS px at any zoom (WCAG 2.2 2.5.8 minimum).
- Mobile-first: base styles small-screen; breakpoints from project scale
  (`size.*` tokens), no ad-hoc px media queries.
- Deep i18n/RTL audits → ultimate-i18n-localization skill.

## Docs per component (assets/component-doc.md template)

Purpose · install/import · API table · variants×sizes×states matrix ·
usage examples (default/hover/focus/disabled/loading/error/dark/long-text/
mobile) · a11y behavior (keys, announcements) · do/don't · themes supported
· known limits. Storybook story per state IF project has Storybook; else
a `*.examples.md`/demo page — docs must exist, Storybook is optional.
