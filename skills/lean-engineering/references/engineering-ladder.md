# The Ladder In Detail — decision procedure and quality floor

The ladder in SKILL.md is binding; this file is the reasoning behind each
rung and the rules that survive every mode.

## Running the ladder

1. **Necessity.** Ask what breaks if the feature/option/layer does not
   exist. Nothing → don't build it, say so in one line. A vague request
   ("build me X") gets the smallest version that does the core job; explicit
   requests are never trimmed by the agent.
2. **Existing implementation.** Grep/read before writing. A helper,
   formatter, component, service or pattern that exists and fits is used as
   the surrounding code uses it — same conventions, same error style.
   Extending a local function beats adding a parallel one.
3. **Extension over replacement.** Prefer growing what is there (a parameter,
   a branch at the shared root) over a second code path — once every caller
   is known. Bug fix: grep every caller of the touched function first; fix
   the root cause once in shared code, not per caller.
4. **Platform/stdlib.** `Array.prototype`, `itertools`, `fetch`,
   `asyncio`, GDScript builtins, Lua stdlib, Blender operators — used before
   hand-rolled. A house component beats a native widget when the project has
   a house component.
5. **Installed dependencies.** Use what `package.json`/`pyproject.toml`/
   manifest already ships. Never add a dependency for a few lines; never add
   a framework, service, wrapper or codegen step without a stated, checkable
   benefit ("needed X because Y; alternative Z rejected because W").
6. **Few readable edits.** The smallest change that ends the task, in the
   structure the codebase already has — its layers, interfaces, conventions.
7. **New abstraction, last.** Only when 1–6 provably fall short, and then
   with the smallest surface that works. Abstraction ahead of the second
   concrete use case is debt.

Decision quality ≠ line count. A labeled 10-line function that replaces a
1-line `eval` needing a decoder ring is the simpler result. The metric is:
can the next maintainer read it without archaeology.

## Understanding before editing (full/ultra)

Before the first edit: read the file(s) to change AND their callers, tests,
fixtures, config, exports, interfaces, and the data that flows through.
Write down (mentally is fine, list is fine) what the change can break — that
list is scope. Extra features are not scope; broken callers are.

## The floor — never traded for leanness

- functional correctness of requested behavior
- input validation at trust boundaries; authn/authz; privacy
- error handling that prevents data loss
- accessibility of UI output
- concurrency/thread-safety the platform requires
- relevant performance constraints; on game stacks additionally:
  frame budget, runtime memory, asset-pipeline constraints, platform limits
  (Defold/Godot/Blender specifics stay with those skills)
- data formats and public APIs (change only when asked)
- platform compatibility; existing test suites (never removed to shrink diff)
- anything the user explicitly asked for

New non-trivial logic (branch, loop, parser, money, security, new script)
leaves a proportionate check: one focused test or an assert-based
self-check. Trivial edits need none. Tests are added where behavior was
uncertain, never deleted to look lean.

## Comments and shortcuts

Comment only the why the code cannot show — one line. A deliberate shortcut
with a known ceiling gets:
`shortcut: <the limit>, <when to upgrade>`.
`/lean debt` harvests these markers; they are tracked, not invisible.

## Mode escalation cost

lite → full → ultra increases scrutiny of the request, never of the
deliverable's completeness. A lite-mode result is still complete; an
ultra-mode result is still shippable. Off only silences the lean rules —
project rules, repo AGENTS files and safety rules keep running.
