# Translation quality & linguistic QA — anti-AI-writing, TM, review states

## What quality means here
A translation passes when a native speaker in the target UI context would
write it that way: correct register (Sie/du per project styleguide), domain
terminology stable across screens, no calque ("Kalte" of "cold start" only if
the project chose that term), natural sentence rhythm, varied openers.

## Anti-AI-writing checklist (per string, target-language)
- no marketing filler ("Erleben Sie nahtlose …") unless the source has it
- sentence lengths vary; not every string starts with the same verb
- meaning preserved: never "improve" content while polishing style
- no literal idioms from the source language
- technical constants, code names, product names stay untranslated

## TM & workflow states
Strings carry status: draft → reviewed → approved. Machine output is `draft`
at most; only a human flips to `approved`. Legal/safety/product-promise text
needs a separate sign-off regardless of quality. TM entries record: source,
target, context, origin (human|mt|tm-reuse), changed-source detection
(stale-flag when source hash changes), reuse count.

## Styleguide + glossary (templates/ ships the seeds)
- glossary.md: term, target(s), do-not-translate flag, per-domain notes
- styleguide.md: register (formal/informal per locale), date/number formats,
  list style, button-case, max lengths per UI zone
Both live in the target project; the skill READS and extends them, never
overwrites existing entries without diffing first.

## Heuristic honesty
Linguistic findings (untranslated-similar, mixed-language, tone drift) are
suspicion-level: MEDIUM/LOW, confirmed=false. They inform humans; they do not
fail builds and are never reported as defects.
