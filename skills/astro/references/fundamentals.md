# Fundamentals — Astro the framework

Astro: HTML-first, TypeScript-first web framework. Ships zero JS by default,
static output by default, islands for interactivity, content collections for
data. Baseline: 7.4.x (7.0 2026-06-22).

## When Astro is the right tool

Use Astro: content/HTML-first sites with optional interactivity — portfolios,
blogs, docs, marketing/product/game sites, i18n sites, headless-CMS frontends,
SSR sites with mostly-static shells. Prefer another stack: canvas/game UI
shells, offline-first SPAs, real-time collaborative dashboards, long-lived
WebSocket-first apps. Recommend the better tool with reasons; never force
Astro.

## .astro anatomy

```astro
---
// 1. Frontmatter: TypeScript, runs once on the server, never ships.
import Layout from '../layouts/Base.astro';
interface Props { title: string; tags?: string[] }
const { title, tags = [] } = Astro.props;
---
<!-- 2. Template: HTML + expressions. Compiler is Rust (7+): NO silent HTML
     correction — unclosed tags / unterminated attrs are ERRORS now. Markup is
     treated as-is; whitespace between inline elements collapses JSX-style. -->
<Layout title={title}>
  <ul>{tags.map(t => <li>{t}</li>)}</ul>
</Layout>

<!-- 3. Optional <style> (scoped by default) and <script> (bundled, hoisted).
     These ARE static-analyzable; keep them small and colocated. -->
<style>
  ul { display: grid; gap: 0.5rem; }
</style>
```

Rules:
- Frontmatter is server-only. Imported data, secrets, DB clients stay there.
- `<script>` in `.astro` is processed/bundled (type="module"); runs on every
  page load where the component renders — only use for what must run always.
- Props are how components receive data; children go through `<slot>`.

## Config — `astro.config.mjs|ts`

Minimal modern shape (verify each key against target docs):

```ts
import { defineConfig } from 'astro/config';
// import adapter only for SSR/hosting targets; none = static host default
// import node from '@astrojs/node';

export default defineConfig({
  site: 'https://example.com',           // REQUIRED for canonical/sitemap/OG
  // output: 'static',                   // default: prerender everything
  // adapter: node({ mode: 'standalone' }), // enables on-demand routes
  // session: false,                     // opt out entirely (>=7.2)
  // cache: { provider: memoryCache() }, // route caching provider (7+)
  // routeRules: { '/api/[...path]': { swr: 600 } }, // declarative caching
  // i18n: { defaultLocale: 'en', locales: ['en','de'], routing: { prefixDefaultLocale: false } },
  // prefetch: true,
  // compressDefault: true,
  // build: { inlineStylesheets: 'auto' },
  devToolbar: { enabled: false },         // agents: disable noise
});
```

Decisions at config level: `output` (`'static'` default vs `'server'` w/
adapter), `site`, `base`, adapter, integrations, image service, i18n,
`session`, `cache`+`routeRules`, `prefetch`.

## Project skeleton (smallest honest start)

```
astro.config.mjs
src/
  pages/index.astro          # routes = files in src/pages
  layouts/Base.astro
  components/
  content.config.ts          # content layer (5+); loaders define sources
public/                      # copied verbatim to dist root
tsconfig.json                # extends "astro/tsconfigs/strict"
```

`npm create astro@latest` scaffolds current defaults — prefer it over hand
rolling, then strip what the project does not need.

## TypeScript contract

- `strict` (via `astro/tsconfigs/strict`) unless project says otherwise.
- `astro check` (from `@astrojs/check`) type-checks `.astro` files; run it in
  CI: `npx astro check`.
- Typing: props via `interface Props`/`type Props` + `Astro.props`; content
  entries typed from collection schema; env via `import.meta.env` (typed by
  `astro/client` types in tsconfig).

## Runtime truth

- Node.js >= 18.17 required on 7.x (verify docs per release; Astro tracks a
  recent LTS band). Rolldown/Rust toolchains ship platform binaries — native
  deps for platform-specific builds.
- Frontmatter runs on server at build (static) or per request (on-demand);
  `getStaticPaths` runs at build; framework components hydrate client-side
  when given a `client:*` directive.
