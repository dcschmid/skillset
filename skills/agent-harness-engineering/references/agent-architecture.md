# Agent Architecture Engineering

Select the simplest architecture that reliably meets the requirement. Complexity
earns its place only with a stated, checkable benefit.

## Pattern catalog (selection first, construction second)

| Pattern | Use when | Cost signal to justify |
|---|---|---|
| Deterministic workflow + model calls | Steps are known ahead | near-zero; keep it |
| Function-calling agent | Structured I/O, single hop | schema discipline |
| ReAct | Path uncertain, observations steer next step | extra turns |
| Hybrid (ReAct plan → typed execution) | Exploration then repeatable execution | recommended default when both matter |
| Planner–Executor | Plan review adds value (approvals, budget) | plan staleness |
| Supervisor–Worker | Subtasks parallelize AND differ | handoff loss, duplicated work |
| Event-based / stateful | Long-running, resumable, external triggers | infra |

Rules:

1. **Detect before proposing.** Read the existing loop, tool table, delegation
   config first (audit_harness.py categories `architecture`, `multi-agent`).
2. **Unnecessary layers** = a model call that cannot change any observable
   outcome, or a delegation whose result the parent re-verifies anyway.
3. **Task decomposition** ends where a step lacks a success criterion. Every
   step declares: done-when, abort-when, budget.
4. **Handoffs** are contracts, not vibes: passing state means a named
   artifact/reference, not re-pasted context.
5. **Delegation chains** deeper than 2 levels need measured evidence of
   benefit; otherwise flatten (see references/multi-agent… sections in
   multi-agent.md).

## State transitions

Explicit states only: `planned → running → (blocked ↔ running) → done | aborted`.
Implicit state ("probably done") is the root of premature-completion failures.
`done` requires the defined criteria to be re-checkable by a tool or test —
verification of the actual result, never a restatement of intent.
