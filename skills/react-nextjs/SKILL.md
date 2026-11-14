---
name: react-nextjs
description: >
  Universal, project-type-agnostic React and Next.js development (baselines: React 19.3.1,
  Next.js 16.4.6, TypeScript, React Compiler; version-gated against the project lockfile at
  task time). Use for ANY task inside a React or Next.js project or any React/Next.js
  question: SPA/Vite apps, App or Pages Router, landing pages, blogs, dashboards, SaaS,
  e-commerce, docs portals, real-time apps, PWAs, component libraries, data-intensive and
  i18n apps; Server vs Client Components, Suspense/streaming, Cache Components and `use
  cache`, proxy.ts vs middleware, Server Functions/Actions, Compiler memoization, hooks
  selection, TypeScript typing, state tooling, design systems, WCAG 2.2 AA, Core Web Vitals,
  SEO/Metadata, testing (Vitest/RTL/Playwright/axe), route/action/cache security, deployment
  adapters, upgrades and migrations. Detects project type, loads only matching references.
  Claims are version-gated; unverified items marked, never invented. Next.js is never forced
  onto projects that fit another stack better.
---

# React & Next.js Development (universal)

Baselines (probe at task start, never trust these numbers over live data):
**React 19.3.1**, **Next.js 16.4.6**, **TypeScript strict**, **React Compiler
(babel-plugin-react-compiler 1.0.0)**, **Node LTS 22.x** — probed 2026-11-14
via npm `latest` dist-tags. Next.js ships version-matched docs inside the
install: `node_modules/next/dist/docs/` (~475 files) — they beat the web for
whatever version the project actually runs.

## Prime Directive

Before changing anything: **read the actual project**. `package.json`
(react/next/typescript versions, package manager), lockfile,
`next.config.ts`/`vite.config.*`/`tsconfig.json` (strict?, compiler options),
`app/` vs `pages/` vs `src/`, existing conventions. Extend what exists; never
build a parallel system beside it. Never invent an API — if it is not in the
version-matched docs or official docs for the installed version, mark it
UNVERIFIED and verify before use. No automatic major upgrades. No experimental
tags without an explicit order.

## Step 0 — Mode gate

| Mode | Trigger | Spine |
|---|---|---|
| **A New project** | empty/blank repo, "create/build a …" | requirements → React-only vs Next.js decision → probe versions → architecture → tooling → scaffold → tests → docs |
| **B Existing project** | repo with code, "add/fix/change …" | read package.json+lockfile+config → versions → conventions → targeted change → relevant tests |
| **C Refactor/optimize** | "slow", "refactor", "modernize" | measure first → risk ranking → small steps → re-measure |
| **D Bugfix** | error, wrong behavior | reproduce → logs/stack → version check → minimal fix → regression test |

Never large refactors where a minimal fix suffices. Full playbooks with gates
per mode: `references/version-policy.md` §modes.

## Step 1 — Stack gate (before any code)

1. **Astro project with React components?** → React rules yes (hooks, types,
   a11y), Next.js rules NO. Do not convert.
2. **Vite/CRA/other React-only SPA?** → React + TS rules yes; App Router,
   Server Components, Server Functions, Next caching = foreign. Do not convert.
3. **Next.js project?** → check major version first (15: middleware.ts,
   fetch caches; 16: proxy.ts, Cache Components, `use cache`). Existing
   project keeps its model unless migration is ordered.
4. **New web project?** pick by shape:
   - content-first, SEO-critical, mixed static/dynamic → **Next.js App Router**
   - pure client app behind a shell, tool, game UI → **React + Vite**
   - already have Astro/other → stay. Framework churn is not an upgrade.

## Step 2 — Load only what the task needs

| Task touches | Read |
|---|---|
| any version/probe question | `references/version-policy.md` (ALSO on first contact with any project) |
| components, hooks, composition | `references/react-core.md` |
| `use`, `useOptimistic`, `useActionState`, `useEffectEvent`, `<Activity>`, `<ViewTransition>`, transition APIs | `references/react-modern-apis.md` |
| memoization, Compiler adoption | `references/react-compiler.md` |
| App Router structure, routes, layouts, metadata | `references/nextjs-app-router.md` |
| Server/Client boundary, streaming, PPR, hydration | `references/nextjs-rendering.md` |
| `use cache`, revalidate/update tags, cache isolation | `references/nextjs-data-caching.md` |
| Server Functions/Actions, forms, mutations | `references/nextjs-server-actions.md` |
| types, generics, unknown, typed APIs | `references/typescript.md` |
| folder/layer decisions, feature layout | `references/architecture.md` |
| CSS, Tailwind, tokens, theming | `references/styling-design-systems.md` |
| state tool selection | `references/state-management.md` |
| APIs, DB, auth, uploads, realtime | `references/fullstack-integration.md` |
| headers, XSS/CSRF/SSRF, secrets, action hardening | `references/security.md` |
| WCAG 2.2 AA, focus, forms, reduced motion | `references/accessibility.md` |
| LCP/INP/CLS, bundles, profiling | `references/performance.md` |
| Metadata, sitemap, locales, RTL | `references/seo-i18n.md` |
| Vitest/RTL/Playwright/axe, release gates | `references/testing.md` |
| package managers, CI, monorepos, lint | `references/tooling.md` |
| adapters, Docker, self-host, env | `references/deployment.md` |
| upgrades, Pages→App, middleware→proxy | `references/migrations.md` |
| AGENTS.md/CLAUDE.md, DevTools MCP, agent loops | `references/agent-workflows.md` |

Working examples you can copy from: `examples/react-vite/`,
`examples/nextjs-app-router/`, `examples/reusable-components/`,
`examples/forms-validation/`, `examples/testing-patterns/`.

## Step 3 — Version gate (binding)

Before using a feature, confirm the floor. Authoritative floors and the probe
commands live in `references/version-policy.md`. Fast facts:

```bash
node -p "require('./node_modules/next/package.json').version"   # installed Next
node -p "require('./node_modules/react/package.json').version"  # installed React
npm view next version && npm view react version                  # latest stable
ls node_modules/next/dist/docs/                                  # version-matched docs
```

`node_modules/next/dist/docs/` outranks the web for the installed version.
`next dev`/`next build` on 16 default to Turbopack; `proxy.ts` replaces
`middleware.ts` (deprecated but functional) — do not write middleware.ts in
new 16+ apps, do keep it in existing 15 apps unless migrating.

## Step 4 — Binding rules (short-form; full rationale in references)

1. **Server Components by default.** `"use client"` only where browser APIs,
   state, or event handlers must live in the browser. Every client boundary
   is a bundle-cost decision.
2. **No reflex memoization.** React Compiler (if enabled) handles
   useMemo/useCallback; adding them by hand is noise or harm. Check whether
   the Compiler is on before writing memo code.
3. **No cache-by-habit.** Every `use cache`/`revalidateTag` needs a stated
   invalidation story. User-specific data needs request-scope or isolation —
   never a shared cache key.
4. **Server Functions are public endpoints.** Validate input, check auth per
   call, no trust in client-sent IDs, no secrets in returned payloads.
5. **State lives at the lowest owner that can see all consumers.** URL for
   shareable state, server for server truth, local for local; a global store
   is a last resort and never auto-installed.
6. **TypeScript strict on new code.** `any` only at typed boundaries with a
   comment; `unknown` + narrowing for external data; typed API responses.
7. **No framework/dependency without a named requirement.** Tailwind, shadcn,
   Zustand, TanStack Query etc. are opt-in with a reason recorded.
8. **Accessibility gates: WCAG 2.2 AA.** Semantic HTML first, ARIA second;
   keyboard path + focus order verified for every interactive component.
9. **Performance claims require measurements.** Profile → change → re-profile.
   No speculative `memo`, no arbitrary `revalidate`, no micro-opts without a
   budget miss.
10. **Migrations are stepped and reversible.** Document breaking changes and
    rollback before running them. No blind codemods.
11. **Docs priority:** version-matched local docs → official docs (react.dev,
    nextjs.org/docs) → release notes/migration guides → repos → community.
12. **Never fabricate an API.** Not documented for the installed version =
    UNVERIFIED = verify or don't ship.

## Step 5 — Ship gate (production claims)

All green or the release is NOT production-ready; report failures as failures:

```bash
npx tsc --noEmit && npm run lint && npm test -- --run && npm run build
```

Plus: critical user flows exercised (Playwright where real), a11y checks
(axe + keyboard), no unexplained hydration errors, no known critical security
findings, perf budget checked against baseline. The 10-point gate and
per-scope command table: `references/testing.md` §release-gate.

## Step 6 — Report

Versions used (actual installed, not assumed) · modules touched · decisions
with reasons (Server/Client split, cache policy, state choice) · verification
output · open items marked UNVERIFIED. Update project AGENTS.md/CLAUDE.md only
by appending; never overwrite existing project rules (`references/agent-workflows.md`).

## Validate this skill

```bash
python3 tests/test_skill.py            # structure + routing + invariants
bash scripts/check-versions.sh [dir]   # project version census (read-only)
node scripts/audit_react_project.mjs [dir]   # stack census (read-only)
```
