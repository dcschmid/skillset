# Long-Term Memory Management

Split (observation-and-context.md): short-term context is compaction-able;
persistent state is not. Memory here = durable state that survives compaction
and session end.

## Rules

- Durable state lives in files/stores with declared access rules — never only
  in the transcript.
- Decisions and open tasks survive compression explicitly: compaction output
  lists them; dropped-but-open work is a defect, not a summary choice.
- References over payloads: persistent notes store paths/ids; the content is
  re-read on demand (and stays untrusted data).
- No secrets in unprotected memory files (security.md protection classes).
- Writes are checkpoints: durable note BEFORE the side effect, so resume after
  interruption replays facts, not guesses (error-recovery-and-reliability.md).

## Store selection (adapter territory, platform-adapters.md)

File-per-note in repo (portable, reviewable) · host memory dirs (Claude Code,
omp) · store APIs (recall/update/delete discipline: update supersedes, no
contradictory twins). Pick one writer per key; conflicts surface as findings in
multi-agent audits.

## Verification

Memory quality gate: after compaction or resume, an agent can answer "what was
decided, what is open, what is next" from durable state alone. Unanswerable ⇒
the compaction lost information — a recovery finding, not a shrug.
