# Pre-Ship Checklist (all project types)

Project-type-agnostic gate. Mark each PASS / FAIL(name) / SKIPPED(reason).
Claiming a line without running it is a reporting bug.

## Engineering
- [ ] `astro check` clean (types, .astro files)
- [ ] `astro build` exit 0; `dist/` matches expected rendering mode
      (flat HTML for static; client+server chunks for adapter)
- [ ] repo lint/format + test lanes green (or absent → noted)
- [ ] preview serves: `/`, one content route, one dynamic/i18n route, `/404`
- [ ] every `client:*` island justified (islands ladder); bundle census sane
- [ ] actions/endpoints validate input; authz server-side

## Content & data
- [ ] collection schemas match real frontmatter; drafts never in `dist/`
- [ ] dates render via `<time datetime>`; images sized+alt'd

## Design & a11y
- [ ] tokens only in components; light+dark contrast pairs ≥ AA
- [ ] keyboard tour: skip-link, nav, forms, dialogs; focus always visible
- [ ] axe on 3 templates clean (or violations listed with fix plan)
- [ ] reduced motion honored; text scales 200%

## SEO
- [ ] `site` set; canonicals absolute; titles/descriptions unique per template
- [ ] sitemap + robots live, URLs 200; OG image on key routes
- [ ] JSON-LD validates on sampled pages; i18n hreflangs mutual

## Performance
- [ ] Lighthouse mobile: LCP<2.5s, CLS<0.1, INP<200ms on key templates
      (or measured deltas vs baseline reported)
- [ ] images: formats/dimensions/lazy-correct; fonts preloaded/subset
- [ ] on-demand routes: caching policy set (cache.set/routeRules)

## Release mechanics
- [ ] envs: secrets runtime-only, `dist/` grep clean; lockfile committed
- [ ] redirects for renamed routes; rollback path named
- [ ] post-deploy checks scripted or listed with owner
