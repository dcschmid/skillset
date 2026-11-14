# Architecture — project layout & boundaries

Scale to the project. The layout below grows in tiers; never impose tier 3 on
a 5-page site.

## Tier 1 — small (portfolio, landing, docs micro)

```
src/
  pages/index.astro, about.astro, blog/[slug].astro
  layouts/Base.astro
  components/Header.astro, Footer.astro, PostCard.astro
  content.config.ts + src/content/blog/*.md
public/
```
All Astro, zero framework deps, static output, no adapter. Done.

## Tier 2 — medium (blog/magazine/product site with CMS or i18n)

```
src/
  pages/            # routes only; thin — fetch + compose
  layouts/          # Base.astro + section layouts
  components/       # ui/ (presentational) + sections/ (page sections)
  features/<name>/  # cohesive feature: component + data + helpers
  lib/              # pure utils: formatting, slugs, fetch wrappers (typed)
  content.config.ts
  middleware.ts     # only when cross-cutting request logic is required
public/
```

## Tier 3 — large (portal, multi-team, SSR app-shell)

```
src/features/<domain>/{components,data,hooks?,server}
src/lib/{api,auth,analytics,...}
src/tests or tests/          # vitest + playwright lanes
src/content.config.ts + multiple collections
docs/ (ADRs, content model docs)
```
Feature folders own their slice: components, data loaders, types. Cross-feature
traffic goes through `lib/` or props/events, never deep imports into another
feature's internals.

## Boundary rules (all tiers)

- **Pages are thin**: parse params, fetch (collections/actions/loaders),
  compose layout+components. No business logic in frontmatter beyond glue.
- **Data access** behind typed functions in `lib/` or feature `data/`: one
  place knows each source (CMS URL, env key, collection name).
- **Components**: props in, markup out; no hidden fetch unless the component
  is explicitly a server island (`server:defer`, >=7 floor check).
- **Design tokens** in CSS custom properties (`src/styles/tokens.css`), not
  scattered literals; themes flip token values, not component CSS.
- **Shared types** in `src/types` only when two+ features need them; feature
 -local types stay local.

## Naming

- Files: PascalCase components (`PostCard.astro`), kebab in `pages/` matches
  URL; `index.astro` for `/`. Collections/lowercase; CSS files kebab.
- Import alias `@/` → `src/` (tsconfig paths) on medium+; small projects use
  relative imports.
- One exported component per `.astro` file; file name = component name.

## Anti-abstractions (do not build)

- Generic "DataFetcher" base classes, per-page duplicate layouts, prop
  drilling through 4 layers where a server island or `Astro.cache` fits,
  client stores for server-owned data, i18n framework on a one-locale site.

## Error handling & state

- Server: throw `Astro.error()` / return typed `{data, error}` from actions;
  pages render fallback UI from data, not blank.
- 404: `src/pages/404.astro` always exists for real projects (see seo.md).
- Client state: local to the island; lifted state only inside the framework
  component that owns it; never global stores for a single widget.
