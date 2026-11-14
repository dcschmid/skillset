---
name: design-system-ui
description: >
    Design-system and UI-component engineering for ANY web project (and
    game-UI concepts for Godot/Defold): CREATE token systems (DTCG v2025.10
    stable), AUDIT existing projects for design inconsistency (duplicate
    colors/buttons/spacing, broken dark mode, unused tokens), FIX safely,
    MIGRATE toward a system, VALIDATE tokens/themes, DOCUMENT components.
    Trigger: design system, design tokens, UI consistency, component library,
    dark mode broken, duplicate components, theme migration, token refactor.
    NOT for: one-off styling without a system (just style it), deep a11y
    (→ accessibility skill), aesthetic originality (→ design-authenticity
    skill), E2E/browser QA (→ ultimate-testing-qa). Ships ds.mjs: zero-dep
    Node CLI (detect/tokens/audit/report) producing file:line evidence.
---

# Design System & UI Components (universal)

Truths (re-probe before spec edits): **DTCG Format Module v2025.10** — first
stable, CG-Final 2025-10-28 (`designtokens.org/TR/2025.10/`); `$themes`/`$media`
conditional rules are still **draft** — NEVER emit them as required output.
WCAG 2.2 AA floor. Node ≥ 18 for `scripts/ds.mjs` (stdlib only, no installs).

## Prime Directive

A design system serves the project's identity — it never replaces it. The
system's vocabulary (tokens, components, states) comes from the project's own
design; where the project has none yet, derive from content/domain, and hand
aesthetic judgment to `design-authenticity`. ds.mjs produces EVIDENCE
(facts, file:line); the agent decides. `confirmed` findings may be fixed;
`heuristic` findings need a human/agent decision first.

## Workflow gate (pick the spine first)

| Workflow | Trigger | Spine |
|---|---|---|
| **INIT** | new project/system | identity → tokens 3-tier → themes → minimal components → docs+tests |
| **AUDIT** | existing project | detect → ds.mjs audit+tokens → triage P0-P3 → report (no edits) |
| **FIX** | audit done, act | batch small → verify each (typecheck/test/visual) → stop on regression |
| **TOKENS** | manage token sources | ds.mjs tokens validate → alias/resolve → no direct edits on generated |
| **COMPONENT** | add/extend one | conventions first → states+API per `references/component-architecture.md` |
| **THEMES** | light/dark/more | one source → parity check → `references/theming.md` |
| **MIGRATE** | legacy → system | inventory → derive tokens → shim old→new → delete legacy when unused |
| **DOCS** | document | component → purpose/API/states/do-don't; Storybook only if project has it |
| **VALIDATE** | quality gate | tokens resolve · themes parity · contrast · tests green |
| **REPORT** | communicate | ds.mjs report md/html, non-destructive (dated suffix on collision) |

Slash-call equivalents: user `/design-system audit` etc. ≡ run this skill in
AUDIT mode. Claude Code/Codex have no slash registry — the table IS the API.

## Shared steps (every workflow)

1. **Detect, never assume.** `node scripts/ds.mjs detect <proj>` → framework,
   styling, token sources, theme mechanism, test runners. Stack rules in
   `references/framework-adapters.md`. Never add a framework/dependency the
   project survives without.
2. **Read project conventions** (existing components/tokens/naming) before
   producing anything. New components MUST match them even if you'd choose
   otherwise (rule 12 of the brief: existing conventions beat taste).
3. **Act in small verifiable steps.** After each batch: typecheck + relevant
   tests + visual spot check. No blind repo-wide search/replace; structural
   edits go through AST tools (ast-grep/LSP) or per-file edits.
4. **Separate source from generated.** `*.tokens.json` (edit) → build step
   (`ds-tokens-build.mjs` in assets/, or style-dictionary if present) →
   generated CSS/TS (never hand-edit). Regeneration must be reproducible.
5. **Gate on release:** P0=0 findings open, tokens resolve, theme parity,
   contrast AA, tests pass. Anything untested ships as NOT TESTED, never PASS.

## Token architecture (binding)

Three tiers, names follow project convention (kebab shown):
`primitives` (raw values, no meaning) → `semantic` (`background-primary`,
`action-primary`, `focus-indicator`; components STOP at this tier) →
`component` (`button-primary-hover`; only when semantic can't express it).
Anti-explosion: new token ONLY if ≥3 uses or a real semantic gap; variants
of one thing that differ in one dimension get a prop or one alias, not N tokens.
DTCG shape + validation: `references/design-tokens.md`; run `ds.mjs tokens`
(cycles/missing refs/type mismatch/theme parity are P0/P1).

## Component quality bar (binding)

Every shipped component: typed API, documented variants/sizes, states
(default/hover/active/focus-visible/disabled/loading/error/empty), semantic
HTML first (ARIA only where native lacks), keyboard + focus management for
overlays, controlled+uncontrolled where interactive, SSR-safe (no window on
server path), no uncleaned listeners. Reuse established primitives
(Radix/React Aria/native `<dialog>`) — never reinvent Dialog/Select when the
project can host one. Full checklist + i18n/responsive rules:
`references/component-architecture.md`. Catalog is a menu, NOT a mandate:
build what's used.

## Game UI (Godot/Defold)

Token *principles* port; web mechanics don't. Theme→Control theme/ThemeItem
re-mapping, gamepad focus maps (no hover — stick/keyboard focus is primary),
HUD/dialog state machines, no `prefers-color-scheme` (in-game theme is a
player setting). `references/theming.md` §game.

## Delegation

a11y depth → `accessibility` · aesthetic originality/generic-design bans →
`design-authenticity` (it owns purple-gradient/glow verdicts; this skill owns
token/component consistency) · browser/E2E harness → `ultimate-testing-qa` ·
framework idioms → `react-nextjs`/`astro` · i18n/RTL depth →
`ultimate-i18n-localization` · big refactors → `ultimate-code-quality-refactoring`.
Unavailable skill → its job degrades to the relevant reference file here;
core duties (audit/tokens/components) ALWAYS stay local.

## Tooling (runs now, zero deps)

```bash
node scripts/ds.mjs detect <dir>                 # stack facts json|md
node scripts/ds.mjs tokens <f.json> [--themes light,dark]  # exit 1 on P0
node scripts/ds.mjs audit <dir> [--format md]    # P0..P3, confirmed|heuristic
node scripts/ds.mjs report <f.json> [--format html] [--out f]  # never overwrite
```
Severity: **P0** functional/a11y-breaking · **P1** major inconsistency ·
**P2** maintainability/debt · **P3** polish. Fix ladder + rules:
`references/audit-rules.md`. Tests: `node tests/run.mjs` (prints VERDICT).

## References (load on demand)

`design-tokens.md` · `component-architecture.md` · `theming.md` ·
`audit-rules.md` · `migration.md` · `testing.md` · `framework-adapters.md` ·
`accessibility.md` · `anti-ai-design-integration.md`
Templates: `assets/` (token source, component doc, audit report skeleton).
Examples: `examples/` (clean + dirty fixture, verified by tests).
