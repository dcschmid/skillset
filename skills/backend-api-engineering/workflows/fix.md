# Workflow: fix (concrete defect)

Input: bug report/500/failing test/audit finding. Output: minimal diff +
regression test + green run.

1. **Reproduce.** Exact failing command/payload; failing test committed
   (or exact manual repro recorded when no runner exists → final status
   carries `NOT TESTED (manual)`). No repro ⇒ no fix.
2. **Root-cause.** Stack → code path → layer owner: data (schema/migration),
   query (DB), logic (service), contract (handler/spec), config (env),
   infra (deploy). Fix the cause, not the symptom; patches that suppress
   errors or weaken checks are forbidden.
3. **Smallest coherent change** in the project's idiom. Exported symbol
   changes: references checked (LSP/grep) first. Neighboring behavior
   preserved unless it is the defect.
4. **Regression test** joins the suite (testing.md protocol): fails on old
   code, passes on new, deterministic, isolated fixtures.
5. **Run:** touched tests → neighboring suite → build/boot. New breaks =
   fix the fix, not the test.
6. **Document** in the change note: defect · cause · diff summary · test
   evidence · status FIXED / PARTIALLY FIXED(+exact remaining command) /
   NOT FIXED(reason+approval needed). Prod DB or deploy steps still gated
   by approval regardless of how green local is.
