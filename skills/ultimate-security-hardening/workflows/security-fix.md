# Workflow: security-fix (FIX MODE)

Input: confirmed findings (this session or prior `security-findings.json`).
Output: fixed code + fix log + verification, statuses per finding.

1. **Preflight** `git status --porcelain`: user changes in target files ⇒
   edit around them (read current content first); dirty tree never reset,
   files never `checkout`'d back. Staged-vs-worktree diffs respected.
2. **Gate each finding** SAFE AUTO-FIX / REVIEW REQUIRED / HIGH-RISK
   (SKILL.md Step 5 table; per-module recipes in
   `references/remediation-guidelines.md`).
3. **Fix** smallest-diff edits per recipe. Language/framework idiom of the
   file wins (boring, native API). No new deps unless the fix requires one
   → then it's REVIEW REQUIRED.
4. **Micro-test** each fix: failing-before/passing-after where a runner
   exists; otherwise exact manual repro payload recorded for the report.
   Security tests join the project's suite.
5. **Project checks**: touched-code unit tests → integration where present
   → build. Breakage introduced here = fix the fix, not the test.
6. **Re-scan** original detector + `run-security-audit.sh` lanes on touched
   paths. New regressions from the fix ⇒ loop to 3.
7. **Log** into `security-fixes.md`: finding id · diff summary · class ·
   test evidence · re-scan result · status
   FIXED/PARTIALLY FIXED/REQUIRES REVIEW/NOT FIXED/FALSE POSITIVE.

## Hard stops (fixes never applied without approval)

prod secrets/rotation · DB migrations/data edits · network/firewall changes ·
deploy-env configs · API contract breaks · algo migrations (hash/session/
token lifetime) · dependency majors · deleting lockfiles/tests · weakening
or globally disabling checks · blanket ignores.

## Exit

Only FIXED counts as fixed (fix + test + re-scan green). PARTIALLY FIXED
list carries the exact remaining step + command for the owner.
