---
name: astro
description: >
  Universal, project-type-agnostic web development with Astro (baseline: Astro 7.4.12
  stable, 2026-11; version-gated against npm at task time). Use for ANY task inside an Astro
  project (astro.config.*, src/pages/, .astro files, content collection config) or any Astro
  question: portfolio/blog/docs/marketing/product/SSR/dashboard sites, SSG vs on-demand vs
  mixed rendering, route caching, server/client islands and hydration directives, Actions,
  sessions, middleware, Content Layer, MDX, headless CMS intake, astro:assets, Fonts API,
  SEO (meta/OG/schema.org/sitemap/RSS), Core Web Vitals and build performance, WCAG 2.2 AA,
  CSP and security headers, adapters and hosting
  (node/netlify/vercel/cloudflare/static/docker), upgrades and framework migrations. Detects
  project type and loads only matching references. Claims are version-gated; unverified
  items marked, never invented. Astro is not forced onto projects that fit another stack
  better.
---

# Astro Development (universal)

Target baseline: **Astro 7.4.12 stable** (npm `latest`, verified 2026-11-14;
7.0 shipped 2026-06-22: Rust compiler, Sätteri Markdown pipeline, Vite 8 +
Rolldown, route caching stabilized). Baselines rot — the version gate, update
routine, and per-feature version floors live in `references/versions.md`.
This skill is **not** tied to any project type: identify the project first,
then load only what the task needs.

## Prime Directive

Before changing anything: **read the actual project**. `package.json`
(Astro + adapter + integration versions, package manager, lockfile),
`astro.config.mjs/ts` (output mode, adapter, integrations, image service,
i18n, session config), `src/` layout, existing components and conventions.
Extend what exists; never build a parallel system beside it. Never invent an
API — if it is not in the official docs for the target version
(https://docs.astro.build/), mark it UNVERIFIED and verify before use.
Astro is chosen when the project is HTML/content-first with islands of
interactivity; a client-heavy dashboard shell or canvas-first app may deserve
another framework — recommend the better tool with reasons, don't force Astro.

## Workflow (every task)

1. **Detect** — project type + rendering needs + hosting target from the
   project or request. One line: `Type: X · Rendering: Y · Hosting: Z ·
   Astro: A.B.C`. Missing info → smallest reversible assumption, recorded.
2. **Version gate** — read the project's Astro version (`package.json`,
   `astro --version` is not a thing: read `node_modules/astro/package.json`).
   New project → latest stable via `npm view astro version`. Load
   `references/versions.md` when a feature is version-sensitive. Never
   migrate an existing project's major version without an explicit decision.
3. **Project audit** — `scripts/audit_astro_project.mjs <project_dir>`
   (read-only, stdlib+node only): config, routes, rendering split, content
   collections, hydration directives, dependency surface.
4. **Route** — pick the minimal reference/workflow set from the tables below.
5. **Plan** — smallest coherent change; name files and routes touched.
6. **Implement** — idiomatic Astro/TypeScript (`references/fundamentals.md`,
   `references/components.md`), existing conventions first.
7. **Verify** — static → build → serve → measure. `astro check`, `astro build`,
   `astro preview`, then the level the task needs. Report each level honestly;
   a green build ≠ working site.
8. **Document** — findings, version gates hit, measured numbers, remaining risk.

## Verification Truth Ladder (report using these levels)

| Level | Means | Proves |
|---|---|---|
| `STATIC` | `astro check`, `tsc --noEmit`, eslint, audit script | types + conventions |
| `BUILT` | `astro build` exit 0 + output inspection (`dist/`, server bundle) | routes compile |
| `SERVED` | `astro preview` / adapter run, routes fetched, status + HTML checked | pages render |
| `MEASURED` | Lighthouse/WebPageTest/runs, timings compared before/after | perf claims |
| `VISUAL` | screenshots/axe run and reviewed | design + a11y |
| `UNVERIFIED` | state it | nothing |

Never collapse levels. No invented build output, no invented Lighthouse
scores. Report the exact command the user runs for any level you cannot run.

## Reference Routing (load only what the task needs)

| Task touches | Load |
|---|---|
| Astro basics, `.astro` syntax, config, TypeScript setup, project type is new | `references/fundamentals.md` |
| folder layout, project size tiers, component boundaries, tokens | `references/architecture.md` |
| SSG vs SSR vs mixed, output modes, adapters, on-demand rendering | `references/rendering-routing.md` |
| routing, params, `getStaticPaths`, middleware, endpoints, redirects | `references/rendering-routing.md` |
| components, props/`Astro.props` typing, slots, server islands | `references/components.md` |
| Content Collections, Content Layer, loaders, schemas, MDX, CMS intake | `references/content-cms.md` |
| client islands, `client:*` directives, Actions, forms, minimal JS | `references/islands-interactivity.md` |
| design, CSS strategy, tokens, Tailwind, dark mode, container queries | `references/ui-ux-styling.md` |
| meta/OG/schema.org/sitemap/RSS/canonical/robots | `references/seo.md` |
| Core Web Vitals, bundle budgets, images, fonts, build timings | `references/performance.md` |
| WCAG 2.2 AA, keyboard, focus, forms, reduced motion, axe | `references/accessibility.md` |
| CSP, headers, sessions/cookies, Actions input validation, secrets | `references/security.md` |
| test strategy, vitest, Playwright, Lighthouse CI, link checks | `references/testing.md` |
| i18n routing, locales, hreflang, localized collections | `references/internationalization.md` |
| framework integrations, adapters, hosting-specific behavior | `references/integrations.md` |
| hosting, adapter choice, CI/CD, headers, rollback | `references/deployment.md` |
| Astro minor/major upgrades, legacy-project migration | `references/upgrades.md` |
| version floors, channel discipline, update routine | `references/versions.md` |

## Workflow Routing

| Situation | Run |
|---|---|
| new Astro site from scratch | `workflows/new-project.md` |
| change in an existing Astro project | `workflows/existing-project.md` |
| new feature/page on an existing site | `workflows/feature-development.md` |
| bug in an Astro site/build | `workflows/bugfix.md` |
| performance or SEO audit pass | `workflows/performance-audit.md` |
| migrate another framework → Astro, or Astro v-latest upgrade | `workflows/migration.md` |
| ship to production | `workflows/production-release.md` |

## Templates

- `templates/component.md` — typed `.astro` component + island shell
- `templates/layout.md` — base layout with SEO/OG/head contract
- `templates/content-collection.md` — collection + schema + loader + page pair
- `templates/project-checklist.md` — pre-ship gate (all tracks)

## Tools

- `scripts/audit_astro_project.mjs` — read-only project auditor (node ≥ 18.17)
- `tests/test_skill.py` — structure + routing validator (this skill's own gate)

## Binding Rules

- Version floors: sessions/actions/route caching/server islands/Fonts API are
  version-gated; state the floor when used (see `references/versions.md`).
  No alpha/beta/canary as defaults.
- Rendering decisions are explicit: every route is static, on-demand, or
  mixed-by-rule — never "whatever the default happens to be" on a mixed site.
- Zero JS by default: a page ships JS only where an island or script is
  required; `client:*` on a component is a decision with a stated reason.
- Existing project conventions beat this skill's preferences; migrations are
  documented, not silently patched around.
- No stale APIs: `getCollection` over legacy `Astro.fetchContent`, content
  layer over `src/content/config.ts` on 5+, Actions over hand-rolled fetch
  endpoints for typed client↔server calls — verified against the target
  version's docs before use.
- Performance and a11y claims come from measurements (`astro check`,
  Lighthouse CI, axe), never from folklore; `astro build --resume` and
  `--verbose`/timing output back build claims.
- CMS/hosting/framework choices are opt-in with reasons; never install an
  integration the task does not require.
- Secrets live in env files/adapters, never in the repo; `.env` stays gitignored.

## Test

```bash
python3 tests/test_skill.py                      # structure + routing (STATIC)
node scripts/audit_astro_project.mjs <project>   # needs node, read-only
```
