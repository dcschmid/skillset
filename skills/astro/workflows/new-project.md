# Workflow: New Astro Project

Applies: zero-to-site. Output: a running, verified Astro project.

1. **Requirements → one line**: `Type: X · Rendering: Y · Hosting: Z`.
   Type from the request (portfolio/blog/docs/marketing/product/game/portal/
   i18n). Hosting unknown → static default, record assumption. Astro-fit check:
   client-heavy app-shell → say so, propose alternative, proceed with Astro
   only if the user insists.
2. **Version**: new project → `npm view astro version` (stable) → that
   version's docs apply (versions.md floors).
3. **Scaffold**: `npm create astro@latest` (strict TS, no demo) OR minimal
   hand roll: `astro` + `@astrojs/check` + TS strict config
   (`astro/tsconfigs/strict`). Package manager: match the environment, commit
   the lockfile.
4. **Architecture**: size tier from architecture.md (default Tier 1; grow
   only on demand). `site:` URL set even pre-domain (placeholder host, TODO
   note).
5. **Rendering**: decision table (rendering-routing.md). Default static;
   adapter only if a route needs per-request data; sessions/actions/islands
   only per the ladder.
6. **Design**: tokens.css first (ui-ux-styling.md), then Base layout
   (templates/layout.md), then pages. Design direction from the brief — no
   house style imposed.
7. **Content**: any collection work per content-cms.md +
   templates/content-collection.md.
8. **SEO/a11y**: head contract wired in layout (seo.md); a11y authored in
   (accessibility.md) — skip-link, landmarks, focus, reduced motion.
9. **Verify (report each level)**: `astro check` → `astro build` →
   `astro preview` + fetch `/`, 404, one content route → lighthouse spot →
   axe on 3 templates.
10. **Deliver**: route list, rendering map, decisions+reasons, verification
    table, next steps (hosting/deploy per deployment.md).
    Stop conditions: missing design direction that changes tokens materially,
    hosting that changes the adapter, CMS credentials absent.
