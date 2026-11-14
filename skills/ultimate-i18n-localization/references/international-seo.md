# International SEO — hreflang/canonical rules enforced by `i18n audit`

Scope gate: only for publicly indexable sites. An offline game or private app
gets ZERO hreflang findings (no false SEO work).

## hreflang contract (Google localized-versions docs)
- every localized page lists ALL its locale alternates + itself (self-reference)
- valid tags only: canonical BCP-47; `x-default` optional for language
  picker/redirect pages; one x-default max
- absolute URLs, no file extensions where the site uses clean URLs
- bidirectional: if A links B, B links A (audit checks within discovered set)
- no hreflang to pages that 404/redirect — crawl-check with the site's own
  server when reachable; static audit cannot claim crawl verification

## canonical contract
- each locale page self-canonicalizes; canonical must never point at another
  locale's URL (canonical-merges-locale = HIGH, confirmed)
- sitemap contains the same locale URLs + xhtml:link hreflang children;
  sitemap tags validated by audit

## locale routing coherence
- default-locale prefix policy stable across the site
- language switcher keeps context (same page, target locale) — no forced
  redirects to home, no redirect chains
- user choice (cookie/persisted) beats Accept-Language

## metadata
localized titles/descriptions per locale; og:locale per locale; hreflang on
error pages only if those pages are served per-locale.

## what the static audit does NOT claim
it does not crawl, so reciprocation beyond the scanned file set and live
redirect loops are out of scope — reported as REVIEW_REQUIRED when the
pattern suggests checking.
