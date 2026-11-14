# Website audit (Mode D)

Tool: `scripts/website_audit.py`. Public URLs only (or `--fixtures DIR`).
robots.txt honoured, redirect chains bounded, response size capped, private/
internal hosts refused unless `--allow-private`. No paywall/login/captcha
bypass; no bulk downloads.

```bash
python3 scripts/website_audit.py https://site.example/about
python3 scripts/website_audit.py https://site.example --crawl --max-pages 50 --max-depth 3
python3 scripts/website_audit.py https://site.example/sitemap.xml --sitemap
python3 scripts/website_audit.py ... --format json --out report.json
```

## What it separates

- **main** — audited per page (blocks outside nav/footer/header/aside/form)
- **chrome** — nav/footer/header repeats: reported once, `scope: site-chrome`
- **thin** — <40 prose words: reported `thin`, never judged

Per page: language, findings (rules + line/col), transparent axis scores,
SEO layer (title/meta/H1/generic link texts), a11y observations (missing alt,
missing html lang, custom interactive hints). Rollup: cross-page repeats,
Du/Sie or register drift, SEO aggregate.

## Reporting honesty

- No JS runtime here: SSG/SSR HTML (Astro, Next, Vue, Svelte) parses fine;
  client-only hydration text may be missed — say so per page when visible
  text count looks low. Trafilatura/Playwright NOT required; if the site is
  client-rendered beyond recovery, report extraction failure, do not guess.
- Scores are finding counts, not quality grades; authorship never asserted.
- Prioritise long audits by estimated reader impact (home > product > blog).

## Audit report shape

`## Website Audit Report` → per page: URL, status, findings with
original/priority/recommendation/rewrite-candidate, then site rollup.
Rewrite candidates are proposals until approved (Mode E).
