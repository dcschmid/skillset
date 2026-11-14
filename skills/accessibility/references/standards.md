# Standards register — status, dates, provenance

Probe date: 2026-11-14. Re-probe before any rules change (see audit-methodology.md §Update workflow).

## Normative baselines (what the skill treats as binding)

| Standard | Status (probed) | Binding use |
|---|---|---|
| WCAG 2.2 | W3C Recommendation, consolidated 2024-12-12 (`REC-WCAG22-20241212`) | A + AA = mandatory floor; AAA = advisory quality goal |
| Understanding WCAG 2.2 | living docs under w3.org/WAI/WCAG22/Understanding | rationale + techniques (informative) |
| WCAG 2.2 quickref | filterable view of SC + techniques | audit checklist source |
| ARIA APG | W3C guide, continuously updated | pattern recipes (informative) |
| WCAG-EM 2.0 | W3C Group Note, 2026-07-23 (`NOTE-wcag-em-2-20260723`) | audit methodology (not normative SC) |
| WCAG 3.0 | Working Draft 2026-09-10 (`WD-wcag-3.0-20260910`) | observation only — NEVER as WCAG 2.2 requirement |
| EN 301 549 V3.2.1 (2021-03) | ETSI harmonised standard | legal mapping for EU procurement (see legal-context.md) |
| BITV 2.0 | in force (DE); cites EN 301 549 | DE public-sector mandate |
| BFSG/EAA | DE implementation of EAA, applies from 2025-06-28 | product/service mandates, partial web overlap |

## Hard rules

1. WCAG 2.2 A/AA are the only mandatory development target. AAA is a
   quality tier reported separately and NEVER allowed to mask an AA failure.
2. Published vs harmonised: EN 301 549 3.2.1 references WCAG 2.1 AA; WCAG 2.2
   adds 9 SC that EN 301 549 has not yet folded in. Meeting WCAG 2.2 AA ⊃
   EN 301 549 web clauses (5.1–5.6 ≈ WCAG 2.1 AA), but the reverse is NOT true.
   A "EN 301 549 pass" ≠ "WCAG 2.2 AA pass". Report both separately when the
   legal context is procurement.
3. WCAG 3 WD items (outcomes, methods, scores) must never appear as
   requirements. Cite as "WCAG 3 draft (2026-09-10)" if mentioned.
4. Automated PASS ≠ conformance. No automated tool run, including this repo's
   `tooling/a11y-audit`, licenses a "WCAG conformant" statement without the
   manual slice (audit-methodology.md).
5. axe-core 4.14.0 tags rules `wcag22aa`; it ships the 5 new WCAG 2.2 SC rules
   (target-size = 2.5.8) and keeps AAA rules default-off — the tool enables
   them per level (tooling/a11y-audit/src/audit.ts).

## Version pin of the tool's rule engine

axe-core 4.14.0 · Playwright 1.65.1 · Node 22.x type-stripping execution.
Guidepup: @guidepup/guidepup 0.40.0, @guidepup/playwright 0.21.0,
@guidepup/setup 0.29.3 (assets under ~/.cache/guidepup — project scope only).

## Update triggers

Re-verify when: axe-core major/minor bump, new W3C WCAG publication (watch
w3.org/TR/wcag/all/), EN 301 549 revision to 4.x, Guidepup release notes
mentioning Orca/NVDA/VoiceOver changes, or every ~90 days. Use
`scripts/check-standards.mjs` (runs network probe + diff report).
