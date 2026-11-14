# Genre rules — priorities differ by text type

Genre decides which rules bind. A README is not a blog; a dialog is not a
changelog. Load one section per task.

## Technical documentation (README, API docs, tutorials, changelogs, ADRs)

Priority: precision, reproducibility, correctness. Voice is minimal, not
absent. Exact commands/paths/versions; no adjectives where a number fits
("2 s faster", not "much faster"). Steps imperative and testable. Changelog:
what changed, for whom, migration note. Forbidden: feature hype, roadmap
poetry. Allowed: dry humor in a comment, a one-line "why" per decision.

## Business communication (email, memo, reports, decisions)

Priority: the ask arrives early; background after. No manufactured
politeness loops ("I hope this finds you well" chains). Du/Sie or register
consistent. Decision docs: options, trade-offs, decision, date, owner.
Repetition of the key number is a bug in summaries, a feature in specs —
know which document this is.

## Editorial (blog, devlog, essays, reviews)

Author voice is load-bearing; preserve quirks found by voice calibration.
Openings and closings vary per article. Concrete beats important-sounding.
Transitions from content, not from a phrasebook.

## Marketing & social (landing, product copy, newsletter, LinkedIn)

Concrete benefit per sentence; every claim checkable (numbers, mechanisms,
named customers if real). No "innovative/solutions/take it to the next
level". CTA names the action ("Download the 4 MB binary", not "Get started
today"). Social: one idea per post; hooks allowed once, not templated.

## UX writing (buttons, labels, errors, onboarding, help)

Accessibility first (see `accessibility-content.md`). Button = action verb +
result ("Save profile"). Errors: what happened, what to do, no blame, no
exclamation marks. Consistency of terms across the product: one object = one
name (never "workspace/project/space" for the same thing).

## Creative → `creative-writing.md` (separate law)
