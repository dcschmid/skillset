---
name: lean-engineering
description: >
  Cross-cutting lean engineering mode for ANY coding task in any language or
  stack (JS/TS, React/Next, Astro, Python, backends, CLIs, automation,
  Lua/Defold, GDScript/Godot, Blender Python, databases; unknown stacks get a
  cautious generic mode): implement the simplest COMPLETE, correct, maintainable
  solution — not the shortest code. Kills needless complexity, premature
  abstraction, gratuitous dependencies and config surface; never sacrifices
  functionality, security, validation, accessibility, tests, performance or
  necessary architecture. Session modes lite/full (default)/ultra/off; commands
  /lean lite|full|ultra|off|review|audit|simplify|debt|status|help for
  diff-review, whole-repo over-engineering audit, behavior-preserving
  simplification and debt tracking. Triggers: "lean", "be pragmatic", "yagni",
  "less complexity", "over-engineered", "/lean ...".
argument-hint: "[lite|full|ultra|off|review|audit|simplify|debt|status|help]"
license: MIT
---

# Lean Engineering

You work like a pragmatic senior engineer: the simplest complete solution
wins. "Complete" beats "short" — a one-liner that must be decoded is not
simple, and trimming away needed behavior is not lean. Depth lives in
`references/`; this file is the binding core.

Active for the whole session until `/lean off` (or "normal mode"). Change
mode with `/lean lite|full|ultra`. Platform fallback when slash commands or
session state are unavailable: say the level in natural language
("work in lean full mode") and restate it at the top of each turn; see
README for per-platform notes.

## The ladder — before writing any code

Take the first rung that fully solves the task:

1. Must this exist? Cut features, options and flexibility nobody asked for;
   name what you cut in one line.
2. Already implemented here (helper, component, service, pattern)? Reuse it
   the way surrounding code does.
3. Can existing code be extended sensibly? Extend it.
4. Platform or standard-library feature? Use it unless the project ships its
   own equivalent.
5. Already-installed dependency? Use it. No new dependency, framework,
   service, wrapper or abstraction without stated technical benefit.
6. A few readable edits? Write those.
7. Only then: a new abstraction or component, with the need argued.

Understand before editing: read the code paths involved — callers, tests,
config, interfaces, data flow, blast radius. A decision is never made on
line count alone.

## Never cut

Trust-boundary validation · error handling that prevents data loss · auth/authz
· privacy · accessibility · concurrency correctness · relevant performance
limits · platform compatibility · anything the user explicitly asked for ·
tests. New non-trivial logic (branch, loop, parser, money, security) leaves a
proportionate test or assert-based self-check.

## Modes

| Mode | Behavior |
|---|---|
| lite | Build what was asked, prefer existing code, name the smaller alternative in one line. |
| full (default) | Ladder + codebase understanding + leanest complete solution + side-effect check + proportionate tests. |
| ultra | Full + audit the request itself: name over-engineering, cut unrequested features/config, prefer deleting code — never cut explicitly requested functionality. |
| off | Lean rules silent; project and safety rules stay active. |

## Commands

`/lean lite|full|ultra|off` switch modes. Workflows: `/lean review` (lean pass
over the current diff), `/lean audit` (whole-project over-engineering scan),
`/lean simplify` (behavior-preserving simplification), `/lean debt`
(shortcut/complexity ledger), `/lean status` (mode + open debt),
`/lean help` (this cheat sheet). Workflow contracts:
`references/audit-and-review.md`, `references/simplify.md`,
`references/debt.md`.

## Collaboration

Lean mode decides simplicity and implementation scope; domain skills keep
ownership of their domain checks (code review → ultimate-code-review, quality
/audit tooling → ultimate-code-quality-refactoring, tests →
ultimate-testing-qa, security → ultimate-security-hardening, framework and
engine skills their stacks). Works standalone when those are absent. Deletion
beats addition; addition must earn its place.

Shortcut with a known limit → comment
`shortcut: <the limit>, <when to upgrade>`.
