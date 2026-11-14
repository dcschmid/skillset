# Google Search guidelines — verified baseline

Verified: 2026-11-14 against developers.google.com/search/docs. Re-verify
before citing as "current" after 2027; update cadence: re-check annually or
on major Google announcement. Sources: Search Essentials, Core Web Vitals
page, structured-data docs, AI features docs.

## Classification levels (use these words in reports)
- **REQUIRED** (essentials): crawlable HTML content, unique titles, working
  status codes, no cloaking, mobile-friendly, no hidden text abuse, valid
  structured data when present.
- **RECOMMENDED**: CWV within good thresholds, sitemap, canonical self-refs,
  meta descriptions, internal linking, schema where content warrants.
- **OPTIONAL/PROJECT**: llms.txt, extra machine-readable files, exotic schema
  types, field-metric pipelines. Offer with justification, never as duty.

## Stable core (rarely changes)
- Content must be in delivered HTML for reliable indexation; Googlebot
  renders JS but with queue/render budget and no guarantees on timing.
  Other AI/LLM crawlers frequently do **no** JS rendering at all.
- robots.txt blocks crawling, not indexation. Pages blocked in robots.txt
  can still be indexed from links ("noindex in robots.txt" is not a Google
  feature). Removal from index = noindex meta / X-Robots-Tag / password / 404.
- Canonical signals: self-referencing default; conflicting signals resolve
  Google-picks-one; don't canonicalize to different content.
- Page experience: LCP 2500ms / INP 200ms / CLS 0.1 at p75, mobile+desktop
  separately (verified thresholds, web.dev/articles/vitals).
- Structured data enables rich results only when it matches visible content;
  fabricated review/rating/FAQ markup is ignored or penalized.
- AI Overviews / AI Mode consume the same index; no separate "AI schema"
  exists. Good answers = clear semantics, extractable facts, citations.

## Commonly wrong in third-party tools (don't cargo-cult)
- "Keyword density targets" — not a Google factor; natural usage only.
- Word-count minimums — none exist.
- Meta description affects rankings — it doesn't (snippet influence ≠ ranking).
- Exact page-speed score thresholds as ranking requirement — CWV is one
  signal among many; site-level lab scores are not a ranking report.
- llms.txt required for AI search — no official requirement (AI-optimization
  guide lists none).
- Indexing API for general pages — restricted to JobPosting/BroadcastEvent.
- "Crawl budget" obsession on small sites — irrelevant below thousands of URLs.

## Update procedure (rules must stay fresh without skill rewrite)
1. `scripts/seo.mjs tools` — probe local tool versions.
2. Re-read the two pages that move: /docs/appearance/core-web-vitals and
   /docs/appearance/structured-data (search-gallery).
3. Diff against this file; edit only changed numbers/behaviors here.
4. Config thresholds live in `config/default.json` — change numbers there,
   prose stays; docs reference both.
