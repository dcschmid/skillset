# Scenarios — worked examples and manual test cases

Each scenario is a reproducible exercise: run the skill in the stated mode
on the fixture and check the listed outcome. These are the acceptance
examples; `tests/test_skill.py` validates the skill's static contracts and
lists these scenarios for manual/agent-driven runs (LLM behavior itself is
verified by inspection, not scripted — nothing here is a fake benchmark).

**S1 · Unnecessary dependency.** Fixture: small JS util `slugify(s)`,
project has no deps. Ask: "add slugify". Expected: hand-written ~5-line
function using existing string APIs; no `underscore`/`lodash` install; one
line naming the lib alternative. Fail: any new entry in package.json.

**S2 · Reuse existing helper.** Fixture: project has
`utils/formatDate()`; task adds a second formatter in a component.
Expected: reuse/formatDate extended; no parallel helper. Fail: two
date formatters after the change.

**S3 · Bugfix with multiple callers.** Fixture: shared `parseConfig()`
with 3 callers, one test. Bug inside. Expected: grep callers first, fix at
the root once, callers/tests updated where the contract moved, test run.
Fail: per-caller patches or untested fix.

**S4 · Duplicate code in existing project.** Two near-identical 40-line
handlers. `/lean audit`: finds them with file:line, proposes extracting
ONE shared path (rung 3, not a framework), states risk + tests. Finding
uses the 7-field table. Fail: table missing fields or invented metrics.

**S5 · Refactor with existing test suite.** `/lean simplify` on a module
with green tests. Sequence honored: baseline → small steps → git diff →
suite green after each; public API unchanged. Fail: rewrite, or API drift,
or suite skipped.

**S6 · Security-critical validation.** Lean-mode task touches a form
handler with input validation. Validation and error paths SURVIVE the
simplification; only pass-through noise is cut. Fail: trimmed validation.

**S7 · Needlessly heavy abstraction.** Interface + factory + registry
around one implementation used once. Expected: name the over-engineering,
propose inline function, deletion preferred over addition. Fail: keeping
the factory "for extensibility".

**S8 · Necessary complex architecture.** Plugin host with genuine second
consumer, versioning requirement, public API. Lean mode says KEEP with
reasons; audit lists it as KEEP row, not a finding. Fail: flattening it.

**S9 · Game code with perf constraints (Godot/Lua/Blender).** GDScript
per-frame loop allocating vectors. Expected: reuse buffers/cached values,
respect frame budget; engine specifics stay in engine idioms; no new addon
dependency. Fail: generic advice ignoring frame budget.

**S10 · Conflict with another skill.** Task also routes to a domain skill
(e.g. security hardening). Division of labor: lean mode sets scope/
simplicity, domain skill keeps its checks; result keeps hardening AND
stays lean. Fail: lean mode deleting hardening, or hardening bloating
scope without need.

Metrics of interest when running S1–S10 against a non-lean baseline:
lines added/removed, new dependency count, test results, regression count,
complexity proxies (nesting, concepts), wall time, tokens where the host
reports them. Record only measured values; unmeasured = N/A. Shorter is
not winning — same behavior with less to read and hold is.
