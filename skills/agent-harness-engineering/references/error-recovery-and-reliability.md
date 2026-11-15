# Error Recovery & Reliability

Machine checks: `detect_loops.py` (traces), `audit_harness.py --only
recovery,reliability` (code). Detection vocabulary below.

## Failure taxonomy

failed-tool-call • invalid-parameters • connection-drop • timeout •
rate-limit • missing-permission • incomplete-task • repeated-identical-error •
infinite-loop • bad-handoff • corrupt-state • missing-dependency.
Anything else is `unknown` → safe-abort path, documented, no guessing.

## Recovery procedures (bounded, always)

- **Retries**: finite max, only when error contract says retryable.
- **Exponential backoff + jitter** for shared-resource pressure (rate limits).
- **Circuit breaker** where a dependency keeps failing: stop calling, report.
- **Checkpoints** before multi-step mutations → resume, not restart.
- **Idempotency check** before re-running anything with side effects.
- **Rollback** offered ONLY when the operation is genuinely reversible —
  otherwise forward-fix with a stated plan.
- **Stop conditions** explicit per loop: budget, attempts, no-progress window.

Binding rules: no endless retries; no auto-retry of irreversible actions
without idempotency proof; a retry must not duplicate side effects; unknown
cause ⇒ safe abort.

## Anti-pattern → control

| Anti-pattern | Detection | Control |
|---|---|---|
| Infinite planning loop | steps grow, no tool call, no artifact | step budget + "produce artifact each turn" |
| Tool call loop | identical (tool,args) N× — detect_loops | progress check before retry |
| Retry storm | consecutive failures, same strategy | change strategy or abort |
| Context pollution | same block recurs; layer overflow | compaction, references |
| Premature completion | "done" without criteria check | verification gate |
| Unnecessary delegation | handoff whose result parent redoes | flatten |
| Excessive chaining | >N calls per user-visible step | macro-tool or workflow |
| Silent failure | except: pass | classify + surface status |
| Hallucinated result | claimed artifact absent on disk | check artifact exists |
| Unverified success | no test/tool evidence | done requires re-checkable proof |

Reporting: an agent marks success ONLY when success criteria are verifiably
met — `done` is a claim a tool can re-check, not a sentence.
