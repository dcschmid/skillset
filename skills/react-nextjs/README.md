# react-nextjs — universal React & Next.js development skill

Agent skill (SKILL.md format: Claude Code, Codex, any SKILL.md runner) for
building ANY React or Next.js web project — SPA, dashboard, SaaS, e-commerce,
blog, docs portal, realtime tool, component library, i18n site — with coding
agents. Baselines: **React 19.3.1 · Next.js 16.4.6 · TypeScript strict ·
React Compiler 1.0 · Node LTS 22** (probe 2026-11-14; version-gated and
re-probed per task, never a frozen number).

## What this is / is not

- IS: router (`SKILL.md`) + 22 references + 5 example sets + 2 working
  read-only tools + static validator; Server/Client-boundary, caching, state,
  security decisions with explicit criteria; measurement-backed perf/a11y/SEO.
- IS NOT: a Next.js evangelist. Astro-with-React and Vite/React SPAs keep
  their stack; Next.js is never forced. No industry, design system, backend,
  or host is assumed.

## Layout (progressive disclosure)

| Path | Content | Loaded |
|---|---|---|
| `SKILL.md` | mode gates, routing table, 12 binding rules, ship gate | on trigger |
| `references/` | 22 deep docs — see below | per routing table |
| `examples/` | copyable idiom snippets per module | when writing code |
| `scripts/` | `check-versions.sh`, `audit_react_project.mjs` (read-only) | at census steps |
| `tests/` | `test_skill.py` static validator (python3 stdlib + node parse) | CI / before commit |

### References (22)

`version-policy.md` (version gate + docs priority + feature floors) ·
`react-core.md` · `react-modern-apis.md` · `react-compiler.md` ·
`nextjs-app-router.md` · `nextjs-rendering.md` · `nextjs-data-caching.md` ·
`nextjs-server-actions.md` · `typescript.md` · `architecture.md` ·
`styling-design-systems.md` · `state-management.md` ·
`fullstack-integration.md` · `security.md` · `accessibility.md` ·
`performance.md` · `seo-i18n.md` · `testing.md` · `tooling.md` ·
`deployment.md` · `migrations.md` · `agent-workflows.md`.

### Examples (per module, framework-current, no external services)

`react-vite/TodoList.tsx` (typed SPA state + effects) ·
`nextjs-app-router/article-page.tsx` (async params, Suspense, metadata) ·
`reusable-components/Button.tsx` (composition + tokens) ·
`forms-validation/rename-form.tsx` (`useActionState` + hardened action) ·
`testing-patterns/examples.ts` (RTL + Playwright).

## Installation & activation

The collection installer symlinks `skills/react-nextjs/` into
`~/.claude/skills/` and `~/.agents/skills/` (see repo README). Activation is
description-matched: tasks naming React, Next.js, components/hooks, App
Router, Server Components/Actions, `use cache`, proxy.ts, web perf/a11y/
testing/migration trigger it; unrelated backend/game tasks do not.

## Use (Claude Code / Codex)

```
Use react-nextjs to add an authenticated dashboard route with cached
article data to this Next.js app.
Use react-nextjs to review the Server/Client split in this Vite React SPA.  ← stays Vite
```

Modes (SKILL.md Step 0): A new project · B existing project · C refactor/
optimize · D bugfix. Each existing project starts with a version census
(`scripts/check-versions.sh`, `node_modules/next/dist/docs/` if present).

## Docs preference (binding order)

1. `node_modules/next/dist/docs/` (version-matched, ships with installed Next)
2. react.dev / nextjs.org/docs for the installed line
3. release notes + migration guides · 4. official repos · 5. community (marked)

## Interop with other skills

Independent; composable. `astro` skill owns Astro projects — React component
rules from `react-core.md` may apply inside Astro islands without converting
the project. Design/testing/deployment skills of the collection layer on top;
no cross-skill imports.

## Maintenance

Re-probe baselines quarterly or on any React/Next major release
(`references/version-policy.md` update routine): probe npm `latest`, refresh
feature floors from official migration guides, re-run
`python3 tests/test_skill.py`, keep the 12 binding rules in SKILL.md stable —
new framework knowledge lands in references, not the router.

## Known limitations

- Static validator: validates structure/routing/invariants, not a live agent
  run (mirrors the `astro` skill's testing level).
- React docs do not ship in `node_modules/react` (unlike Next); react.dev is
  the ceiling there.
- Feature floors encode the 2026-11 stable line; verify per installed version
  on older projects before assuming an API exists.
