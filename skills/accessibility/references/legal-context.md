# Legal / regulatory context (as of 2026-11-14; not legal advice)

Layers — keep them separate in reports:

1. Technical standard: WCAG 2.2 (W3C Recommendation). A/AA/AAA are technical
   levels, not legal outcomes.
2. Harmonised European standard: EN 301 549 V3.2.1 (2021-03) — the version
   harmonised for EU procurement. Web clauses 5.1–5.6 ≈ WCAG 2.1 AA clauses.
3. National law:
   - EU WAD (Directive 2016/2102) → public sector bodies: WCAG via EN 301 549
     (DE: BITV 2.0 §3 references EN 301 549 "Stand der Technik").
   - EAA (Directive 2019/882) → BFSG (DE) from 2025-06-28: consumer-facing
     services/products (e-commerce checkout, banking, e-books…), not general
     websites.
   - US: Section 508 (agencies) references WCAG 2.0 AA; ADA case law often
     cites WCAG 2.x.

## Reporting rules derived

- EN 301 549 ≠ WCAG 2.2: EN 301 549 3.2.1 predates WCAG 2.2's 9 new SC;
  meeting 2.2 AA satisfies web clauses (5.x) but cite levels per document:
  "WCAG 2.2 AA satisfied; EN 301 549 (WCAG 2.1 AA subset) satisfied".
- Non-web (desktop, mobile native, games): EN 301 549 clauses 5.1–13 apply
  via platform APIs (see native-platforms.md) — do not paste web WCAG pass
  statements; ICT product ≠ website content.
- Automated test output is evidence, never a legal claim. A report may state:
  "automated checks pass; manual slice outstanding; no conformance claim made."
- BFSG applies to transactional flows (order buttons, checkout forms) with
  focus on operability, NOT full AA site-wide; distinguish in scoping.
- Public sector DE: BITV 2.0 + BGG; federal guidance:
  bundesfachstelle-barrierefreiheit.de (EN 301 549 references, BFSG papers).
- ETSI: EN 301 549 maintained by ETSI TC HF; watch EN 301 549 v4.x (drafting
  to track WCAG 2.2/3 — verify at etsi.org before relying).

## When asked "are we compliant?"

Answer format: "Against WCAG 2.2 A/AA: <result> on tested scope <pages/states>
with tools <x> and manual pass <y>; remaining manual items: <list>. Conformance
claims need WCAG-EM sample; this is audit evidence, not a declaration."
