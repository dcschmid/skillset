# Workflow: verify (contracts/tests/migrations/quality gate)

Input: "check everything", pre-release gate, post-audit confirmation.
Output: verdict per quality-gates.md ladder with command evidence.

1. **Enumerate targets:** suites present (detect-project.sh), spec files,
   migration dirs, deploy manifests. Anything absent ⇒ listed `NOT TESTED`
   in score, never assumed.
2. **Run in order** (fail fast per stage, report per stage):
   static (typecheck/lint) → unit → integration (DB via test harness) →
   API contract (spec validation: `validate-openapi.py`, drift vs impl) →
   migrations (up/down seeded, review lint) → authz matrix → e2e/smoke
   → build/boot → `/healthz` `/readyz` probes. Use the project's runners;
   missing tool = gap recorded, fallback = project-native equivalent, not
   silent skip.
3. **Fix what verification exposes** via workflows/fix.md (safe tier);
   re-run the failed stage after each fix.
4. **Verdict:** category table + evidence paths per quality-gates.md; hard
   gates evaluated first; `PASS` only ≥90+green+evidenced, else
   CONDITIONAL/FAIL/INCOMPLETE with the exact next command per open item.
