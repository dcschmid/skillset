# AI Coding Agents & MCP — agent-native workflows

## Existing rules win

A project's `AGENTS.md`/`CLAUDE.md` (and this skill) coexist: **append or
edit surgically; never overwrite** project rules. Next.js 16+ ships agent
surface: version-matched docs in `node_modules/next/dist/docs/`, official
first-party skills/agent rules for its own workflows — use those for
framework depth; this skill routes to them (version-policy.md priority 1).
Check which are installed before duplicating.

## Next.js agent mechanisms (verify availability per installed version)

- **Version-matched docs** (always present, offline): first stop for any
  framework question (version-policy.md).
- **DevTools / browser loop:** run `next dev`, drive real browser checks
  (Playwright MCP or project's browser tooling) for visual/hydration proof
  before claiming UI done.
- **Official skills (e.g. cache-components optimization, dev loop)** — if
  available in the agent's skill set, load the matching one instead of
  restating framework internals here.

## Working modes (agent-optimized)

- **Analysis:** read census first (scripts/*), then change; report file
  inventory with versions (version-policy.md probes).
- **Small packages:** one committable slice per increment, gate each
  (testing.md); no multi-concern mega-diffs.
- **Bugfix:** reproduce → minimal fix → regression test (SKILL Step 0-D).
- **Review:** diff against invariants (SKILL Step 4 list) + release gate
  commands.

## MCP & external tooling policy

Install/invoke MCP servers, official skills, and agent integrations ONLY when
(a) available in the environment, (b) version-compatible, (c) the task needs
them. Otherwise the file-based workflow (this skill + local docs) is complete.
Never invent an MCP tool name; never assume DevTools MCP presence.

## Handoff documentation

Every non-trivial session updates: version facts used, decisions + reasons
(server/client split, cache policy, state choice), gate command outputs,
UNVERIFIED list. AGENTS.md additions: project commands + conventions only —
the kind of facts that save the next agent a repo tour.
