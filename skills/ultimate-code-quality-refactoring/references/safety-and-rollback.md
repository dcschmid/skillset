# Safety & Rollback

Foreign work is sacred. The skill's own hunks are revertible; everything else
is untouchable.

## Before any edit

1. `git status --porcelain` — enumerate user changes; edits must not collide
   with them. Collision → stop, report conflict, keep both.
2. Scope the change: file list + intended hunks stated before editing.
3. Baseline captured: `verify_changes.py --save-baseline` with the project's
   check commands.
4. No commit, no push, no branch/stash/commit deletion, no `reset --hard`,
   no `clean` — ever, unless explicitly asked.

## Risk classes

- **LOW** (behavior-preserving, single-file, provable): apply in fix modes,
  verify immediately.
- **MEDIUM** (multi-file / interactions): characterization tests first; each
  step verified; stop on any new failure.
- **HIGH** (architecture, public API, DB, concurrency, permissions,
  production-critical logic): written proposal + explicit approval BEFORE
  touching code.

## Failure protocol

1. Isolate the failing step (last diff).
2. Diagnose: was it the edit or the baseline? Compare to baseline failures —
   PRE-EXISTING stays attributed to baseline.
3. One safe correction attempt; re-verify.
4. Not fixable → revert ONLY the skill's own hunks
   (targeted `git checkout -- <file>` of files it solely edited, or reverse
   patch). Mixed files (user+skill edits): manual hunk revert or stop.
5. Report what was reverted and why.

## Provenance

Every report distinguishes: measured / proxy / hypothesis / unverified.
Rollback safety claims require the diff to be skill-only. No safe separation
→ change stops, conflict is the deliverable.
