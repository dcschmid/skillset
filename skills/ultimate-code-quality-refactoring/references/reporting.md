# Reporting

Reports are for the engineer who acts on them tomorrow. Facts, heuristics,
and recommendations stay visibly separate. No synthetic positivity.

## Audit report (see assets/audit-report.md)

1. Executive summary — project shape, top findings, gate status.
2. Project overview — languages/frameworks (from detection bundle).
3. Findings — each: `file:line` evidence, class, priority, risk, effort.
4. Architecture — dependency/boundary evidence or "no structural findings".
5. Debt backlog — seeded table (technical-debt.md schema).
6. Duplicates — candidate groups + merge verdicts.
7. Hotspots — measured proxy table from `collect_metrics.py`.
8. Verification — executed checks vs baseline; UNVERIFIED items listed.
9. Recommendations — prioritized, small packages.
10. Roadmap — ordered independent packages.

Large projects: compact summary in chat, detail files under the project's
docs (non-destructive, dated suffix on collision).

## Change report (after edits, see assets/before-after-report.md)

changed files · per-change description + intent class (REFACTOR/BUGFIX/
FEATURE) · before/after measured table (`compare_baseline.py` output only) ·
tests executed with verdicts · rollbacks performed · residual risks · open
packages.

## Style rules

- Numbers only from bundle/delta output; missing = N/A.
- Proxy metrics labeled "proxy"; hypotheses labeled "hypothesis".
- Pre-existing failures keep their own column — never blamed on the change,
  never hidden.
- PASS requires executed checks; no checks → UNVERIFIED section, report still
  ships.
- Optional score: formula published inline or no score at all.
