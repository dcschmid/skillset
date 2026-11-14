# Project Discovery — automatic analysis of existing projects

Purpose: first step of every existing-project mode (AUDIT, AUDIT_AND_FIX,
DESIGN_MODERNIZATION, ANTI_AI_SLOP_CLEANUP, VISUAL_REGRESSION_REVIEW).
Read-only. Use what exists; install nothing new when the project's own
infrastructure suffices. Respect project instructions (AGENTS.md, README,
docs) and existing architecture decisions.

## Detection matrix (read files, don't ask)

| Signal | Where to look | Feeds |
|---|---|---|
| Framework | `package.json` deps (astro, react, next, vue/svelte), `astro.config.*`, `next.config.*`, engine project files (game grids/GUI: `defold-development`/`godot` skills own those stacks) | scope, run command, framework skill handoff |
| Build system | package manager lockfiles, `tsconfig`, scripts (`dev/build/preview/check`) | verification commands |
| Styling architecture | global css, CSS Modules, Tailwind config, styled-components/emotion, UnoCSS | consistency checks, token location |
| Design tokens | `tokens.*`, theme files, `:root` custom props, tailwind `theme`, library theme providers | preservation inventory, edit surface |
| Component libraries | imports (shadcn/MUI/Radix/…), `components/ui` dirs | reuse-first fix plans |
| Routing | `src/pages`, `src/routes`, `app/`, router config | route inventory for scope |
| Layout components | `layouts/`, `Layout.astro`, `_app`, root layouts | shell-level checks |
| UI tests | test dirs, playwright/vitest/cypress deps, screenshot suites | reuse for verification, never duplicate |
| A11y tooling | axe, the `accessibility` skill's tooling, existing a11y configs | audit handoff (never re-run blindly) |
| Browser tooling | playwright/puppeteer cached browsers | rendered audit; absent → source fallback |
| CI | `.github/workflows`, other CI | gate fit (§ CI) |
| Conventions | lint configs, formatter, commit style, component naming | all edits match them |

## Output (internal, 5-15 lines)

`framework · build-cmds · styling-model · tokens-location · components-root ·
routes(count) · test-cmds · browser(available|absent) · ci(present) ·
conventions(2-3) · preservation-list`. Missing layers → say "not present",
never invent. Large projects: sample representative routes (home, primary
task, auth, admin, edge states) — coverage is stated, not assumed.

## Runnability probe

`build`/`dev` command exists? Node/deps installed (lockfile + node_modules)?
Dev server boots? Server won't start → source-only audit, documented; NEVER
claim rendered evidence.

## Selective scope resolution

`whole project | route | page | component | mobile-only | desktop-only |
dark-only | a11y-only | authenticity-only | visual-regression |
changed-files (git diff)` — resolve against routes/component map above.
Small change → never audit/rebuild the whole site.
