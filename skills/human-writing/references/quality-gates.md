# Quality gates — 11 checks, bounded loops

Run after every rewrite pass; max 2 passes, then ship the better of pass 1/2.
Gate failure = fix the text or revert; never grind to pass 3.

| Gate | Question | Fail action |
|---|---|---|
| 1 Meaning | Same claims, negations, hedges? | Revert span |
| 2 Facts | Numbers/names/quotes intact? | Revert span |
| 3 Substance | Any checkable claim present or reported missing? | Report missing info, never invent |
| 4 Naturalness | Would a careful native say it to this reader? | Re-draft span |
| 5 Voice | Matches profile/genre register? | Re-draft toward profile |
| 6 Rhythm | Varied lengths where prose, not spec? | Split/merge one sentence |
| 7 Anti-slop | No clusters left (see patterns-core)? | Edit cluster, keep devices |
| 8 Context | Fits genre + surface (doc vs blog vs story)? | Reload genre guide |
| 9 SEO/a11y (sites) | Headings, alt, label, meta, links honest? | Fix per seo/accessibility refs |
| 10 Technical integrity | Protected spans, builds, tests green? | Manual patch, stop |
| 11 Editorial | Whole text readable, credible, worth the reader's minutes? | Ship or tell user what's missing |

Scores from `hw_report.scores` are counting aids for gates 3/6/7 only;
quality beats score. Gate 10 outranks gates 4–7 for site content: a
structurally damaged page is never "improved".
