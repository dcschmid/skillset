# Documentation standards

Binding rules for every artifact this skill writes. Scripts enforce what is
machine-checkable; this file governs judgment.

## Evidence tiers

Every technical statement carries one tier; lower tiers never dress up as
higher ones:

1. **VERIFIED** — you ran/read the source: code, config, tests, lockfile, CI.
2. **DOCUMENTED** — stated by a project file (manifest, existing doc, ADR).
3. **PLAUSIBLE** — consistent with evidence, unconfirmed → write as open
   question or `REVIEW_REQUIRED`, never as fact.
4. **UNKNOWN** — no basis → name it as unknown; absence of docs stays a gap,
   not a fabricated section.

Checks report `PASS | WARN | FAIL | REVIEW_REQUIRED | NOT RUN`. A check that
never ran is NOT RUN. Automated PASS is not a quality claim.

## Diátaxis routing

Pick ONE mode per document; mixing is the top readability failure:

| Mode | Reader task | Voice | Test |
|---|---|---|---|
| Tutorial | learn | guided, no choices | works end-to-end first try |
| How-to | accomplish X | imperative steps | goal verifiable at the end |
| Reference | look up | neutral, complete | matches code exactly |
| Explanation | understand | discursive | no imperative instructions |

Tiny projects: a README with install+run+test is complete; do not bolt on an
`/explanation` tree to hit a template.

## Style (prose layer belongs to human-writing)

- Lead with the action or the fact; no throat-clearing ("This document
  describes…", "In today's…", "It is important to note…").
- Concrete nouns, verifiable numbers, real paths. Delete adjectives that
  survive only to flatter ("seamless", "robust", "powerful").
- One idea per sentence in steps; imperative mood in how-tos.
- Terminology: reuse the project's own words (routes stay "routes", not
  "endpoints" when the code says routes). Fix a term per concept across docs.
- DE/EN: keep code identifiers, product names, CLI flags untranslated;
  localize navigation and prose only.

## Structure rules

- Heading hierarchy contiguous (h1→h2→h3); exactly one h1 per file.
- Link texts name the target ("Install guide", not "here"); alt text on
  meaningful images; no color-only meaning (WCAG 2.2 AA baseline for docs
  sites — a11y skill owns formal audits).
- Commands: copy the exact string from the project's scripts/CI, run when
  environment-safe. Linux (incl. Fedora), macOS, Windows split ONLY where
  commands differ; note the pkg-manager difference rather than assuming apt.
- Diagrams versionable as text (Mermaid/plantuml/C4); every node maps to a
  real component; decorative diagrams are defects.

## Repair discipline (docs-fix)

Priority order: P0 secrets exposed → P1 wrong/unrunnable commands, broken
links → P2 stale or missing essential content → P3 structure/consistency →
P4 cosmetics. Correct the P0/P1 set first; preserve working prose; never
rewrite a whole file to apply one fix; unverifiable fixes ship as findings.
