# Upgrades & Migration — version-gated, reversible

Two jobs: bump Astro within/between majors; move a foreign project to Astro.
Existing functionality is the contract; upgrades are a user decision.

## Astro upgrade workflow (vN → vN+1 or minor)

1. **Baseline**: project version (`node -p
   "require('astro/package.json').version"`), adapters/integrations pinned
   versions, `astro check` + `build` green now (the reference point).
2. **Read the docs**: https://docs.astro.build/en/upgrade-astro/ per-version
   guides — breaking changes, removals, new defaults; feature floors in
   versions.md.
3. **Branch** + upgrade: `npx @astrojs/upgrade` (official codemod CLI) or
   `npm install astro@<target>` + matching adapters/integrations (majors move
   together).
4. **Migrate mechanically**, known 7.x surface:
   - Rust compiler: no more silent HTML correction — unclosed tags/unterminated
     attributes now error; fix templates; whitespace collapses JSX-style.
   - Vite 8/Rolldown: custom `esbuild`/`rollupOptions` config auto-converted;
     exotic Vite plugins verified per plugin.
   - Markdown: Sätteri default — remark/rehype plugin chains re-verified.
5. `astro check` → `astro build` → preview smoke diff (route list + key pages
   HTML) vs baseline; then the lanes in testing.md.
6. Commit per concern (config, templates, deps); document each breaking change
   hit + fix in the PR.
7. No alpha/beta/canary targets; `latest` = stable only (versions.md).

Rule: a failing step returns to the smallest fix that restores baseline —
never rewrite unrelated code "while upgrading".

## Foreign project → Astro (framework/CMS migration)

1. Inventory routes + content + interactivity (audit script + crawl existing
   site: sitemap, status codes, forms, dynamic blocks).
2. Classify per route: static / on-demand / island (rendering-routing.md
   decision table) — preserve current behavior first, optimize later.
3. Content: source → content layer loaders/schemas (content-cms.md), keep IDs
   stable for URL parity; redirect map for changed URLs.
4. UI: port design tokens → tokens.css (mechanics identical); components port
   Astro-first, framework islands only where state exists.
5. Parity checklist: routes 1:1 (or redirect map), SEO tags equal-or-better,
   forms/actions work, a11y lanes pass, Lighthouse ≥ baseline (measure both).
6. Ship behind the same host or migrate host in the same change (deployment.md).

No big-bang rewrites: migrate section by section when the site is large;
mixed old/new served during transition with redirects.

## Dependency updates (non-Astro)

One lane at a time (integrations, then adapters, then libs): `npm outdated` →
per-package changelog → bump → tests green → commit. Peer-dep conflicts resolved
by choosing the combination matching the Astro baseline, never `--force`.
