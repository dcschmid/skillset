# Audit methodology (WCAG-EM 2.0, Group Note 2026-07-23)

Scope of THIS section: how a full audit is scoped, run, and reported.
WCAG-EM itself is a methodology Note, not normative SC.

## Phases (WCAG-EM 2.0 → our mechanics)

1. Define scope — audience, technologies, environments (browsers × AT matrix
   declared up-front, incl. what we CANNOT test here: see screenreaders.md).
2. Explore the website — crawl routes, classify page types (tool: `a11y audit`
   per route template).
3. Select samples — representative pages per type + states (dialog, error,
   empty, loading, mobile viewport). Our config: routes[].scenarios.
4. Prepare detailed audit plan — SC × page-type applicability table. AAA gets
   its own table (wcag-aaa.md) — NEVER merged into AA results.
5. Audit sample pages — automated (`a11y audit` AA+AAA levels) + keyboard
   (keyboard-testing.md) + manual per-page checklist + real SR where host
   allows (screenreaders.md evidence contract).
6. Report outcomes — statuses per SC and per page: PASS / FAIL /
   NEEDS MANUAL REVIEW / NOT APPLICABLE / NOT TESTED.
   Missing ≠ PASS. Automated PASS ≠ conformance.
7. Repeat on fixed pages (after remediation) — `a11y compare --before --after`
   is the formal re-audit diff.

## Sampling honesty rules

- dynamic states: an unopened dialog is NOT audited content; run scenario steps
- auth routes: fixture login with env-placeholder credentials
  (`${A11Y_USER}`), never real creds in config/reports
- if a page-type sample cannot be reached: page-type = NOT TESTED with reason
- AT matrix: environment probe via `a11y check` (check environment probe)

## Gate vs conformance (release gate contract)

- CI gate = deterministic: axe AA violations = exit 1. This is the release gate.
- Conformance statement = gate + manual queue closed + SR evidence where
  declared. Template in legal-context.md; keep both in the report.
- AAA progress report separate section; satisfied/violated/N-A/review per SC;
  gate unaffected unless `--strict-aaa` explicitly requested.

## Update workflow (standards drift)

- trigger: axe release, W3C pub, EN 301 549 revision, 90-day cadence
- `scripts/check-standards.mjs` fetches status pages, diffs against
  references/standards.md pinned values, emits CHANGE report
  (old → new, source, impact on rules/tests/skill). No auto-editing of
  normative docs from unverified third-party sources.

## Severity mapping (report vocabulary)

- blocking: confirmed AA violation on audited scope
- serious: SR/keyboard breaks core task (SR evidence + manual)
- advisory: AAA, best-practice, or heuristic (target-size off-spec sizes)
- review: automated needs-review (incomplete) — never silently counted

## Report content contract (every full audit)

project · date · standards+versions (pinned) · pages+states · browsers+OSes ·
tools actually run · automated results · manual results · SR results (or
"none, host unsupported: <why>") · open/untested SC · severity · affected
user groups + impact · locations · SC refs · repro steps · fixes+CODE ·
re-test status.
