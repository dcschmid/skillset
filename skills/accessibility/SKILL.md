---
name: accessibility
description: >
  Universal accessibility engineering and auditing (WCAG 2.2 A/AA binding, AAA
  as separate quality tier; W3C Recommendation 2024-12-12, probed 2026-11-14).
  Use for ANY accessibility task on ANY surface: plan/build/review/test/fix
  a11y in HTML/CSS/JS/TS, React, Next.js, Astro, Vue/Svelte, SPAs/SSR/SSG,
  webshops, dashboards, forms, design systems, component libraries; audits of
  existing projects; WCAG-conformance questions; screenreader/keyboard/focus
  testing; remediation of found issues. Ships a real runnable audit tool
  (TypeScript + Playwright + axe-core, JSON/HTML/JUnit/SARIF, level-aware AAA,
  scenario scanning, CI exit codes), a keyboard/focus auditor, Guidepup/Orca
  screenreader harness with honest environment gating, and reference docs for
  WCAG2ICT/native/mobile. Framework skills (astro, react-nextjs) own framework
  specifics; this skill owns the accessibility layer across all of them.
  Automated PASS ≠ conformance — reports always separate automated gate from
  manual and SR evidence.
---

# Accessibility Engineering & Auditing (universal)

Baselines (re-probe before rule changes; see `references/standards.md`):
**WCAG 2.2** (Rec. 2024-12-12) A+AA binding, AAA advisory tier · **ARIA APG**
current · **WCAG-EM 2.0** (Group Note 2026-07-23) for audits · **EN 301 549
v3.2.1** for EU/BFSG/BITV mapping · axe-core 4.14.0 · WCAG 3.0 = Working
Draft, observation only, NEVER a requirement source.

## Prime Directive

Fix the source, not the scanner. Accessibility is decided by semantics,
keyboard, contrast, and announcements — not by ARIA sprinkles. Every claim in
a report maps to evidence: automated run, keyboard walk, manual check, or
real screenreader speech. Missing tests are reported as NOT TESTED, never
as PASS. Never claim conformance from an automated run alone.

## Mode gate (pick the spine first)

| Mode | Trigger | Spine |
|---|---|---|
| **A Build** | new UI/component/page | semantics → keyboard → contrast → states → tests |
| **B Audit** | existing project, "check/audit" | WCAG-EM scope → sample → tool run → manual queue → report |
| **C Remediate** | issues found/open | reproduce → locate → verify SC → minimal fix → re-run → regression test |
| **D Advise** | question | answer from references, cite SC, mark AAA vs AA |

## Workflow A — Build (every UI change)

1. Read project: framework, lint config, existing patterns (`package.json`,
   component conventions). Load matching `references/framework-integration.md`
   section.
2. Native semantics first: `<button>/<a>/<input>+<label>/<dialog>/headings/
   tables` — ARIA only for platform gaps (`references/aria-patterns.md`).
3. Wire states: visible `:focus-visible`, expanded/selected/error states in
   attributes, status via `role=status`, errors via `aria-describedby`.
4. Surface rules: contrast tokens (4.5/3.1 AA, 7/4.5 AAA), targets ≥24 px
   (44 touch), reflow 320 px, reduced-motion/contrast honored
   (`references/do-dont.md`).
5. Add tests with the change: component keyboard test (focus in/return),
   route in tool config for `a11y audit` (CI lane below).
6. Gate before done: run tool + manual keyboard pass on changed surface.

## Workflow B — Audit (WCAG-EM 2.0 slice)

Full protocol `references/audit-methodology.md`. Mechanics:

```bash
cd tooling/a11y-audit && npm install            # once (axe 4.14, playwright 1.65)
node bin/a11y.mjs check                          # environment capability matrix
node bin/a11y.mjs audit --url <url> --level aa   # single URL, desktop+mobile
node bin/a11y.mjs audit --config a11y.config.json --level aaa --format json,html,junit,sarif
node bin/a11y.mjs keyboard --url <url>           # focus traversal (DOM evidence)
node bin/a11y.mjs report <results.json> --format html
node bin/a11y.mjs compare --before a.json --after b.json   # after fixes
node tests/screenreader-orca.ts                  # real SR where host allows
```

Config = routes + scenarios (dialog open, menu, error, login via `${A11Y_*}`
env placeholders — secrets never land in reports). AAA findings report as a
separate block; gate stays AA unless `--strict-aaa`.

## Workflow C — Remediate

reproduce → locate code → confirm SC (`references/wcag-aa.md` per line) →
smallest fix preserving design intent → regression test → `a11y compare`
before/after → update report statuses. Scanner-appeasing patches banned.

## Report contract (every full audit)

Statuses: PASS / FAIL / NEEDS MANUAL REVIEW / NOT APPLICABLE / NOT TESTED.
Sections: scope+date+versions+tools · automated results · manual queue
(NOT silent) · SR evidence or "host unsupported: <reason>" · severity +
affected users + repro + fix+CODE · re-test. CI gate PASS ≠ WCAG conformance
claim (`references/legal-context.md` answer template).

## Binding rules

1. A/AA from WCAG 2.2 = mandatory; AAA separate tier, never masks AA; AAA
   claims only per-criterion (`references/wcag-aaa.md`).
2. Automated "needs review" (axe incomplete) = NEEDS MANUAL REVIEW, never
   pass; DOM/AX-tree/virtual-SR results are NEVER called screenreader tests
   (`references/screenreaders.md` test-type table).
3. No a11y overlays as fixes; no aria-hidden over focusables; no outline
   removal without replacement; placeholder is not a label.
4. Native/desktop/game targets: WCAG2ICT + EN 301 549 mapping, never web WCAG
   claims (`references/native-platforms.md`).
5. BFSG/EAA/BITV scope ≠ site-wide AA scope; distinguish procurement docs
   (EN 301 549 ⊉ WCAG 2.2 delta) in reports (`references/legal-context.md`).
6. Standards drift: `scripts/check-standards.mjs` + 90-day cadence; human
   review before normative edits; pinned versions in references/standards.md.
7. Framework skills stay authoritative for framework APIs; this skill owns
   a11y requirements and tooling — no duplicated framework docs.

## References (load per need)

`references/standards.md` pins+provenance · `wcag-aa.md` all-A/AA dev checks
· `wcag-aaa.md` tier template · `do-dont.md` patterns+antipatterns ·
`aria-patterns.md` widgets · `screenreaders.md` SR matrix+Fedora/KDE/Wayland
truth · `keyboard-testing.md` focus audit · `framework-integration.md`
React/Next/Astro · `native-platforms.md` WCAG2ICT · `legal-context.md`
EN301549/BFSG/BITV · `audit-methodology.md` WCAG-EM+gates. Tool: `tooling/
a11y-audit/` (src, fixtures, tests). Setup: `scripts/setup-check.sh`.
Validation: `python3 tests/test_skill.py` → VERDICT PASS/FAIL.
