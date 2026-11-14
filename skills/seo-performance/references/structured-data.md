# Structured data — validation & discipline

Three verdict tiers, never collapsed (schema.mjs):
1. **valid-schema** — parses, types/fields exist per schema.org.
2. **google-conform** — matches Google feature docs (required fields for the
   rich-result type); subset of what's valid.
3. **rich-result-award** — whether Google shows the rich snippet:
   UNDETERMINED offline; needs Rich Results Test / live SERP.

`scripts/seo.mjs schema <target>` prints tiers + issues + content cross-check.

## Required-field floor (Google feature docs, verified 2026-11-14)
| type | required for rich result |
|---|---|
| Article/BlogPosting | headline, datePublished, author |
| Organization/LocalBusiness | name (+url; LocalBusiness+address) |
| BreadcrumbList | itemListElement[] (positioned, named) |
| Event | name, startDate, location |
| Product | name, description (+offers for price snippet) |
| VideoObject | name, uploadDate, thumbnailUrl |
| WebSite/WebPage | url (+SearchAction for sitelinks searchbox) |
Full curated set in `schema.mjs KNOWN`; schema.org has 800+ — unknown types
warn, not error.

## Rules
- JSON-LD preferred, in <head> or body; one block per entity is fine;
  @graph for multi-entity.
- Only mark up what is visible on the page (content cross-check: name/
  headline/ratingValue must appear in visible text or flagged
  not-in-visible-text).
- Absolute URLs; dates ISO-8601, dateModified ≥ datePublished.
- No fabricated Reviews/Ratings/Offers/FAQ. If the site has no reviews,
  emit no review markup — absence is correct, fabrication is wrong.
- Framework emission: Astro components (head.astro), Next metadata/JSON-LD
  components, React <script type="application/ld+json"> in returned JSX.

## Validation ladder
offline `schema <target>` → Schema Markup Validator (validator.schema.org) →
Google Rich Results Test (search.google.com/test/rich-results) → live.
Skill stops at tier 2 + instructs tiers 3 on request; never claims awarded.
