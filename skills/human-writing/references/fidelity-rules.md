# Fidelity rules — what a rewrite may never touch

Gate order for every Mode B/E edit. Violation = revert, not explain.

1. **Meaning** — same claims, same direction (cause stays cause), same
   negations, same hedges that carry truth ("usually" stays "usually").
2. **Facts** — numbers, dates, versions, names, quotes verbatim; units and
   precision unchanged (`3.5 MB/s` never becomes `~4 MB/s`).
3. **Structure** — code fences, inline code, links + hrefs, images, tables,
   frontmatter keys, footnotes, heading hierarchy preserved; only prose inside
   editable spans changes.
4. **Voice profile** — the author's quirks (found via voice-calibration) beat
   any style rule; you edit around them.
5. **Missing facts** — if text has no content under the filler ("innovative
   solutions"), report what information is missing; do NOT invent a product,
   price, or feature to fill the hole.
6. **Terms** — domain terminology and established project vocabulary stay
   (see also protected regions in `website-rewrite.md`).

Minimal-diff principle: change the smallest span that fixes the finding. A
rewrite that shuffles untouched good sentences is a failed rewrite even if
every new sentence is fine.

## Good-text rule

Good sentence → untouched. Audit modes list candidates; they do not earn the
right to churn. Repeated application must converge (pass 2 output equals pass
1 minus nothing).
