# Workflow: Project review (pre-merge / handoff)

Read-only pass over changes; every finding carries a verification level.

## Checklist

1. **Version honesty** — `project.godot` `config/features` + CI pins match
   declared engine (4.7.x per `references/godot-versions.md`); no beta
   features presented as stable.
2. **Structure** — tree matches `architecture.md` (or project's own layout);
   autoloads few/typed; no parallel framework; new files placed per existing
   conventions.
3. **Data integrity** — audit script: no broken `res://` deps, no missing
   scripts, `.import` committed, save payloads versioned.
4. **Style contract** — new visuals obey style refs (filtering/stretch/
   materials/theme); asset budget deltas called out.
5. **Code** — typed public APIs, signals over polling, `delta`-correct motion,
   no `get_node` in hot loops, no swallowed errors.
6. **Gates** — requested/changed behavior has evidence at ≥ the level claimed;
   performance changes carry before/after numbers; UNVERIFIED items listed
   with their commands.
7. **Risk ledger** — migrations touched, settings changed, addons added
   (compat/license), platforms affected by renderer/shader edits.

## Output

Findings table: file · level · finding · severity · suggested fix. Verdict:
ship / fix-first / needs-engine-verification (with commands). Never vibes.
