# Workflow: Production Release

Gate everything; deploy is the last 10%.

1. **Freeze**: branch/commit cut; changelog draft (features, content, perf,
   breaking changes for hosts).
2. **Full gate** (testing.md lanes that exist): `astro check` → lint →
   `astro build` → preview smoke (all route classes incl. 404 + i18n locales
   if any) → tests → axe on 3 templates → Lighthouse vs budget → SEO crawl
   (sitemap/titles/canonicals). Each lane: PASS/FAIL/SKIPPED (reason) —
   honestly.
3. **Host preflight** (deployment.md): envs set (secrets server-only, grep
   `dist/` bleed), `site:` = production URL, headers (security.md baseline),
   redirects live, cache policy (route caching / hashed assets).
4. **Deploy** via the host's pipeline (never local-to-prod rsync unless the
   host is a plain VPS — then artifact + healthcheck + rollback copy).
5. **Post-deploy verification (MEASURED)**: `/` + key routes 200, robots/
   sitemap live, one action/form round-trip, one i18n locale, Lighthouse on
   production vs pre-deploy artifact.
6. **Rollback plan**: previous artifact/build id named; CMS/schema changes
   get a written back-out note. State it in the release notes.
7. **Report**: gate table (honest levels), deploy id, post-deploy checks,
   rollback command/path.
