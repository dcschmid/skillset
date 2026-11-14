# Workflow: audit (existing backend)

Input: any project. Output: prioritized findings + applied fixes (safe
ones) + verification. Report-only on fixable items = failure.

1. **Profile.** `scripts/detect-project.sh <proj>` + read entrypoints,
   routes, migrations, configs, CI. Classify new/productive/legacy/
   partially-modernized with evidence. `git status` first — user changes
   respected, never reverted.
2. **Twelve areas, each with evidence** (finding schema
   `templates/finding.json`, severities CRITICAL→LOW):
   1 API architecture/consistency (errors, versions, contracts) →
   api-design.md · 2 DB design + query perf (`EXPLAIN` sampled on hot
   routes) → database-engineering.md · 3 AuthN/AuthZ: IDOR sweep over
   every `{id}` route + tenant scoping → authorization.md · 4 Security:
   injection/validation/secrets/CORS/deps → security.md (deep → ultimate-
   security-hardening) · 5 error handling · 6 caching · 7 scalability
   ceilings → architecture.md · 8 resource use/pools · 9 logging/
   monitoring gaps → observability.md · 10 deploy/config → deployment.md ·
   11 deps/tech debt (lockfiles, majors) · 12 test coverage vs mandatory
   scenarios (testing.md). Missing runner = coverage gap `NOT TESTED`,
   never pass.
3. **Prioritize.** CRITICAL/HIGH = user-facing breakage, exploitable,
   data-loss risk. Each finding: file/component · defect · evidence ·
   root cause · impact · fix · change-risk · validation method.
4. **Fix ladder.** SAFE (tests missing, missing ownership check, N+1,
   missing index, unvalidated input, no timeout) → fix now via
   workflows/fix.md. REVIEW (schema change, framework swap, new infra,
   contract break) → patch proposed, not applied, approval asked.
5. **Re-audit touched areas** (tests + detect diff + plans) → score per
   quality-gates.md with evidence per category; gates decide verdict, not
   points.
