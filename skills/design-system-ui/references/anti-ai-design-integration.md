# design-authenticity boundary (cooperation, no overlap)

Split of duties (both skills stay independent — either works alone):

| Question | Owner |
|---|---|
| "Is it consistent, tokenized, complete-state, maintainable?" | design-system-ui (this skill) |
| "Is it generic? Purple-gradient/anywhere-rounded/glow-spam/dashboard-clone?" | design-authenticity |
| Is the palette itself on-brand / original | design-authenticity picks/verdicts → this skill tokenizes + keeps consistent |
| Which states a component has | this skill (bar) · what states LOOK like | design-authenticity |

## Handoff protocol
1. NEW system (INIT): identity/visual-language pass runs FIRST
   (design-authenticity CREATE flow if installed) → its output (palette,
   type voice, radius/shadow posture, motion character) becomes the INPUT
   to token derivation. No identity pass available → derive from
   content/domain, note it.
2. AUDIT: report keeps two buckets — consistency findings (this skill fixes)
   vs identity findings (hand list to design-authenticity; e.g. "these 3
   accents compete" = consistency, "all accents read generic-SaaS" = them).
3. FIX: never flatten personality while normalizing — merging two card
   components preserves the deliberately distinctive one; merging hexes
   keeps the brand value, not "the nearest indigo".

## Local defaults when design-authenticity is absent
Still binding on this skill (identity-preserving subset of its bans):
no unprompted purple gradients / global glow / blanket rounded-everything;
no template dashboard layout as a "component default"; motion only where
it communicates state. These live here because tokenizing generic output
faithfully is still garbage-in-garbage-out.

## Quality-score note (reporting §22 of brief)
Score categories here measure SYSTEM quality (tokens/components/consistency/
tests/docs). Aesthetic points belong to design-authenticity's rubric —
reports cite it, never blend the numbers.
