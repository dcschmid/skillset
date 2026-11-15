# Multi-Agent Coordination

Detection: `detect_loops.py` (handoff ping-pong), `audit_harness.py`
(`multi-agent` category; skipped when no delegation config exists).

Roles — **examples, not a default shape**: supervisor, planner, executor,
reviewer, validator, specialist, aggregator.

## First question

Does more than one agent beat one? Evidence required: parallelizable AND
differing subtasks, or independent verification with different context.
Otherwise: one agent, smaller harness.

## Coordination contracts

- **Assignment**: one owner per task unit; task = id + scope + done-when +
  budget. Two owners = duplicated edits (finding).
- **Communication**: messages carry artifact references, not pasted context.
- **Shared state**: single writer per key, or merge rule declared before
  parallel work; uncontrolled concurrent file writes are a finding.
- **Aggregation**: validator re-checks artifacts on disk; aggregation over
  claims is how hallucinated results survive release.

## Failure modes (all detected or reported)

Mutual endless delegation (ping-pong cycle in trace, indices reported) •
duplicate task execution (same task id, two owners) • contradictory edits
(same file, two writers, no merge rule) • lost intermediate results (no
checkpoint before handoff) • overhead without benefit (delegation count vs
measured outcome delta — when unmeasurable: UNVERIFIED, not 0).

Handoff = state transition with evidence attached, bounded by the same retry
and stop rules as any other step.
