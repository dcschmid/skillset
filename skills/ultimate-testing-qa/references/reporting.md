# QA report contract

One report per delivery. `node scripts/qa.mjs report results.json
--format md,html` → renders below; collisions get timestamp suffixes,
never overwrite.

## statuses (closed set)

PASS (ran, green, evidence linked) · FAIL (ran, red, defect located) ·
NEEDS REVIEW (evidence seen, human call needed: visual diffs, a11y
incomplete, copy) · NOT TESTED (not run + reason: offline WebKit, no auth
creds, page not reachable) · N/A (doesn't exist on this surface).
Automated PASS ≠ conformance/quality claims; NOT TESTED ≠ PASS.

## results.json shape (input to qa.mjs report)

```json
{ "project": "acme-shop", "source": "playwright 1.65.1 + vitest 5.1.0 run 2026-11-14",
  "results": [
    { "name": "checkout journey (chromium)", "status": "PASS",
      "detail": "4 steps + validation error path", "evidence": "test-results/checkout-chromium/",
      "fix": null },
    { "name": "webkit engines", "status": "NOT TESTED", "detail": "browser binaries offline" } ],
  "retest": ["2026-11-14 cart-total FAIL→PASS after money.cents fix (vitest related src/lib/money.ts)"] }
```

Every row: evidence pointer (dir/file/command), fix pointer when the
fix-retest loop ran. Scores only when the suite computed them — never an
invented number, never averaged across automated+manual.

## Sections (md/html output, see assets/qa-report.md skeleton)

1. Scope+stack+versions+date (what could NOT run)
2. Results grouped by status, tier-1 journeys first
3. Fix-retest log (before→after per defect)
4. Manual review queue (NEEDS REVIEW, never dropped silently)
5. Coverage map + uncovered risk · 6. Next actions with owners

## Cadence artifacts

- PR lane: `vitest run --changed` + journey specs; verdict in PR comment.
- Main/nightly: full matrix + visual baselines update policy.
- Trace/video/screenshot dirs uploaded as CI artifacts; report links them.
- `qa.mjs analyze` md output is the strategy section of the first report.
