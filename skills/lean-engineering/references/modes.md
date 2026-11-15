# Modes — activation, session behavior, per-platform notes

## Definitions (binding)

| Mode | Adds over previous | Guarantee |
|---|---|---|
| **lite** | nothing beyond default good practice | task built as asked; existing code preferred; smaller alternative named in one line, user decides |
| **full** (default) | the ladder + understand-before-edit + side-effect check + proportionate tests | leanest *complete* solution; behavior, safety, tests intact |
| **ultra** | critique of the request itself | over-engineering named; unrequested features/config cut; deletion preferred — explicitly requested functionality NEVER cut |
| **off** | — | lean rules silent; project, repo and safety rules stay active |

Mode is session-scoped and sticky: it survives compaction of the chat but
not `/lean off`. Restate the active mode when a new task starts after a long
break if the host dropped context.

## What each mode changes in behavior

**lite** — the agent answers the request normally, prefers existing code,
and appends at most one line naming a smaller viable option ("could drop X
and still meet the ask — say the word"). Nothing is silently dropped.

**full** — the ladder runs before any new code; callers/tests/config are
read first; after editing, the diff is checked against the blast radius;
the project's own test/lint commands run where they exist (failure =
baseline or fix, attributed honestly).

**ultra** — before building, each part of the request is checked against
the actual need; parts with no justification are reported and skipped (not
silently: named, so the user can overrule). Existing over-engineering in
touched code is flagged, removed only in the touched path. Reports name the
complexity removed and the evidence it was dead.

**off** — the ladder, floors and reporting rules above no longer bind;
everything the repo and platform require still does.

## Activation per platform

- **Claude Code** — install symlinks the skill into `~/.claude/skills/`;
  `SKILL.md` frontmatter carries `argument-hint` so `/lean <mode>` appears
  with completion where the host renders skill arguments. Natural-language
  activation ("lean full mode on this repo") works identically.
- **OpenAI Codex / agentic CLIs** — skill discovered from the skills root;
  no native slash-command registry is required: the commands are phrases.
  "`/lean audit src/`" typed as plain text is matched by the skill
  description. Session persistence = the mode statement restated in the
  conversation.
- **oh-my-pi / generic hosts** — skill list is the registry; activation by
  naming the skill or any trigger word. Where the host has no session state,
  the mode is restated per turn ("lean mode: full" as the first line) and
  the rules bind for that turn.

No platform adapter files are shipped: there is nothing runtime to adapt.
The skill is instructions plus tests; adapters would be the first piece of
unnecessary complexity.
