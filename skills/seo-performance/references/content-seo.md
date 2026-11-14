# Content SEO & human writing

Evidence-first, substance-preserving. If `human-writing` skill exists,
delegate prose rewriting there; this layer diagnoses and proposes diffs.

## Assessed per page (content scope: `seo.mjs content <target>`)
structure: h1 count, heading hierarchy, semantic landmarks, section
depth vs word count; metadata: title 10-70ch unique, description present,
og/twitter counts; substance: visible word count, orphan status, internal
links, breadcrumbs.

## Quality signals (report as observations, not scores)
search intent match, information density, redundancy (duplicate
descriptions/boilerplate), stale dates, missing sources, readability
(prose vs filler). AI-slop markers flagged when reworking text: interchangeable
intros, empty marketing phrases, keyword repetition, mechanical cadence,
generic conclusions, impersonal voice.

## Hard rules (binding)
- no keyword-density targets, no artificial word minimums;
- no invented experiences, references, expertise, testimonials;
- preserve brand voice, existing terminology, technical meaning;
- edits to substance need a source; large rewrites go as proposal + diff;
- never replace human prose with mechanical SEO text.

## Text proposal format (for review, not auto-apply)
```
<!-- seo-perf:proposed title --> old → new (+rationale)
<!-- seo-perf:proposed description --> …
<!-- seo-perf:rewrite <selector> --> diff of body (preserve meaning)
```
Applied only on approval; content-removal is always approval-gated.

## Site-type emphasis (activate by detection, not blanket)
blog: author/publish-date/related-links · SaaS: feature+docs+pricing
intent · ecommerce: product/variant/category schema, filter-URL canonical
strategy · portfolio: project case depth · docs: versioned canonicals,
heading depth. Skip irrelevant checks — blanket advice is noise.
