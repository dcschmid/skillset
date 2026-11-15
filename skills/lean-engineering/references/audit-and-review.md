# Review & Audit workflows — /lean review, /lean audit

Both are read-only by default: they report; edits happen only through
/lean simplify or on explicit ask. Findings are evidence-first — every one
carries a `file:line` (or range); an unavailable judgement is stated as
"not checked", never guessed. Not every abstraction is over-engineering:
judge each inside its project context (why was the layer added, what
second caller does it serve, what does the platform require).

## /lean review — the current change (diff scope)

Input: `git diff` (staged+unstaged) or the named files. If the repo is not
git, the user names the touched files.

1. Read the change plus its callers, tests, config, exports.
2. Run the ladder over the diff: new dependency? new abstraction before a
   second use? duplicated existing helper? config option with one value?
3. Check the floor survived: validation, error handling, tests for new
   non-trivial logic, a11y on UI output.
4. Output, per finding: `file:line` · problem · why it is needless here ·
   smaller alternative · risk of changing it. Then: verdict
   SHIP / SHIP-WITH-TRIMS / TRIM-FIRST, and one line on what was not
   checked. Nothing invented; complexity claims cite the measured shape
   (n callers, n config keys, nesting depth).

## /lean audit — whole project

Default read-only scan. Scope: what the user names, else the source tree
(dir count, manifests, test command discovered from files, never assumed).

Hunt list (each finding needs evidence, not vibes):

- duplicate or unused functions/exports; components with zero callers
- dependencies used for < a handful of lines, or unused entirely
- abstraction with one implementation and no second use in sight
- redundant components/wrappers around a stdlib/platform call
- config options nobody varies; flags with one value in every environment
- stale workarounds for versions the project no longer supports
- overcomplicated data flow: layers that only pass values through
- needless network/DB round-trips (N+1, fetch-all-then-filter)
- control flow unreadable in one pass (deep nesting, flag arguments)
- error handling larger than the operation it guards
- architecture layers with no responsibility; special cases that grew
  more special-casing than the general path

Report table, one row per finding — the seven required fields:

| # | where (file:line) | actual problem | why needless here | proposed simplification | risk | expected benefit | tests needed |
|---|---|---|---|---|---|---|---|

Rules:
- "why needless" answers in project terms (single caller, unused knob,
  dead since version X), not "because shorter".
- risk + tests-needed state what breaks and which existing check proves it;
  if no test exists, say "no coverage — characterization test first".
- benefit is what shrinks (lines, deps, round-trips, concepts a newcomer
  must hold) — measured where measurable, else labeled estimate.
- Architecture that demonstrably earns its keep is reported as
  KEEP (with the reason), so the audit is a balance sheet, not a hit list.
- Priority order P0 breaks-without-it → P3 cosmetic; only P0/P1 are worth
  acting on this week.

Execution: grep/tree-walk + language tools already in the project. No new
dependency for the audit itself; if a scan is too large to read fully,
state coverage ("top 40 files by churn") instead of claiming completeness.
Delegating heavy scanning to an existing project tool (or the
ultimate-code-quality-refactoring scripts, when installed) is preferred —
same repo, same evidence bar; results are re-checked against this list
before reporting.
