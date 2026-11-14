# Workflow: regression-verification (VERIFY MODE)

Re-check prior fixes (own or third-party) against current tree. Produces
test results + corrected finding statuses. Never trusts old reports: the
code may have moved on.

## Ladder (each FIXED finding)

1. **Still present?** read the fixed location — fix intact, reverted, or
   partially reapplied (reverted ⇒ finding re-opens, status NOT FIXED, note).
2. **Regression test exists?** run it (project runner: vitest/jest/pytest/
   go test/cargo test/dotnet test — detection from `detect-project.sh`).
   None yet and finding still relevant ⇒ author now (before/after proof via
   git stash is forbidden on dirty trees; use a scratch copy or mark the gap).
3. **Detector rerun** on the component: semgrep rule / fallback scanner lane.
4. **Neighbors**: run the project suite for the touched module (fix-induced
   functional regressions are the classic failure).
5. Status rewrite: all green ⇒ FIXED (+test ref); test failed ⇒ PARTIALLY/
   NOT FIXED with failure evidence; test absent but re-scan clean ⇒
   PARTIALLY FIXED (test gap).

## Test quality bar (authored security tests)

- assert the security property AND the legit path (both directions)
- deterministic, isolated, no network/prod data, synthetic creds only
- one flaw one test, named for the flaw (`idor-user-a-cannot-read-b`)
- joins existing suite layout; fails loudly when the flaw returns

## Ledger per verification

finding id · fix present (y/n/partial) · test ran (+output ref) · detector
reran · suite result · final status · residual risk one-liner. Aggregate →
report `security-test-results.md`; verdict feeds release-gate.
