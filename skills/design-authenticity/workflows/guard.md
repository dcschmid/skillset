# Workflow: GUARD

Inline mode while an agent writes UI code during ordinary development. Light by
design: catches obvious slop early without hijacking the task. Auto-engages on
UI-relevant edits (styles, components, layouts, themes); stays silent on
backend/logic/non-visual work.

## Loop (per UI-relevant change, seconds not phases)

1. **Context check:** new files only, or riding existing tokens? Existing
   system → ride it; do not "improve" untouched neighbors.
2. **Scan** the change (not the repo) for `anti-ai-patterns.md` A–J quick hits:
   default violet-blue gradients, unchosen system-font-everywhere, hero+3-cards
   skeleton, decoration stacks (blur+glow+radius+shadow), card-per-section,
   invented copy, meaning-less color, focus-invisible states, no reduced-motion
   on motion, desktop-only layout.
3. **Fix in place** findings that are `major`+ against THIS product's context;
   keep `minor`/`nit` as one-line notes in the delivery summary. No side quests,
   no new files beyond what the task needs.
4. **Floor check** before calling done: a11y floors hold
   (`accessibility-integration.md`), responsive state sane, render reviewed if
   a browser was already running. Never claim a check not run.

## Non-blocking rules

- One pass per logical change; no re-scan loops (full review belongs to REVIEW).
- Trivial styling (rename, single spacing token) → no ceremony.
- Existing deliberate style wins over this engine's taste.
- When the task is a full page/design system, escalate to CREATE.
