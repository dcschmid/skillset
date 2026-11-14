# Workflow: Migration & Upgrade

Two modes — pick one: (A) Astro version upgrade, (B) foreign project → Astro.
Both follow upgrades.md mechanics.

## A. Astro upgrade (e.g. → current stable)

1. Baseline green (check+build+tests recorded) — the rollback anchor.
2. Read per-version upgrade guides + breaking-change list; feature floors per
   versions.md. Alpha/beta channels: never.
3. Branch; `npx @astrojs/upgrade` where offered, else pin astro+adapters+
   integrations to the matching set.
4. Migrate mechanical breaks in steps: config keys → content layer (5.x) →
   templates (7.x strict markup) → markdown plugins → custom vite config.
   Commit per concern.
5. Full verification: check → build → preview all route classes → repo tests →
   Lighthouse compare (7.x should not regress; it usually improves).
6. PR: version table before/after, breaking changes hit, fixes, measurements.

## B. Foreign framework/CMS → Astro

1. Inventory (URLs, content sources, interactivity, SEO tags) —
   `scripts/audit_astro_project.mjs` post-scaffold, crawl tool pre.
2. Behavior parity plan: per route static/on-demand/island; URL parity +
   redirect map; content model → collections/loaders with stable ids.
3. Port tokens + layouts, then components (Astro-first; islands per ladder).
4. SEO/a11y parity checklist per route class (seo.md, accessibility.md).
5. Ship parity gate: route parity test, tag parity test, Lighthouse ≥
   baseline, redirect map live. Big sites: section-by-section, old+new served
   together during transition.

## Both modes

- Never "while here" rewrite unrelated code; never keep shims after the
  cutover; documentation of behavior changes ships in the PR.
- Blocked ≠ failed: missing CMS creds / unknown host target → recorded open
  question, proceed on the smallest reversible assumption.
