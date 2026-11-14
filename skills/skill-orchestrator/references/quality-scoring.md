# Quality scoring — 100 points, verifiable only

Eight weighted categories. Deductions come exclusively from validator
findings and discovery facts. Nothing is checked → scored 0 credit and
listed under `unchecked` (never automatic full marks).

| Category | Pts | Backing checks |
|---|--:|---|
| Structure & standards | 15 | meta.*, structure.*, size.* |
| Activation & routing | 20 | content.activation (+ description triggers) |
| Content quality | 20 | content.* |
| Security | 15 | security.*, secret.* |
| Tests & reliability | 15 | `has_tests` fact (no tests → 0 + UNCHECKED) |
| Maintainability | 10 | body size vs references/ split |
| Efficiency | 5 | orphan references |

Severity → deduction within category: `error` full, `warn` 0.5×,
`info` 0.15×.

## Grades

90–100 Excellent · 80–89 Good · 70–79 Needs Improvement · 50–69 Poor
· <50 Critical.

## Blockers override the number

A security `error` or invalid required metadata is a blocker regardless
of total: the grade caps at Poor (≤69) and the blocker is listed verbatim.
Reproducing this repo's truth: several skills currently exceed the 1024-char
description limit (verified real finding, not a tool artifact) — a genuine
standard violation the owner may or may not fix; the tool reports it, does
not hide it.

## Score is not a verdict

A number never replaces a test result. `test --all` runs the tiers; the
score is a quality *signal* alongside them. Report both or neither.
Agent-eval tiers, when no agent CLI is installed, report `UNAVAILABLE` —
that is honest gating, not a 0.