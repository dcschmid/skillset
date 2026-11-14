# Developer guide — <project-name>

Goal of this guide: <one concrete outcome the reader can verify>.

## Prerequisites

<from manifests; versions verified, e.g. `node -v` against lockfile engines>

## Setup

1. `<command copied from package.json/pyproject/Makefile — run it once to verify>`
   Expected: <observable output>.
2. `<next command>` — Expected: <output/state>.

Platform notes: Linux/Fedora `<pkg mgr cmd>`; macOS `<cmd>`; Windows `<cmd>` — only where steps actually differ.

## Daily loop

- Dev server: `<cmd>` → <port/URL>
- Tests: `<cmd>` · single test: `<cmd with arg, verified>`
- Build: `<cmd>` → artifact at <real path>

## Debugging

| Symptom | Where to look | Fix |
|---|---|---|
| <real error string> | <file/config> | <change/command> |

## Extending

Add a <module/route/feature>: touch <files listed from tree>; register at <real registration point>; test in <test dir>.

## Not yet covered

<NOT RUN / UNKNOWN areas, named so the next reader does not trust them>
