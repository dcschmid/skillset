# defold-development — universal Defold game-dev skill

Agent-skill (open format, works with Claude Code, Codex, and any
`SKILL.md`-compatible runner): genre-, art-style-, and project-independent
engineering guidance for the **Defold** engine, baseline **1.14.1 Stable**
(`ee283d4`, 2026-11-10).

## What this is / is not

- IS: a router (`SKILL.md`) + deep references + workflows + opt-in project
  profiles + working, non-destructive scripts, all version-gated and honest
  about stable vs beta vs "requires an extension/manual work".
- IS NOT: a racing/low-poly/Riff-Racers skill. Riff Racers is one optional
  profile; genre systems ship only when a project asks for them.

## Layout

| Path | Content | Loaded |
|---|---|---|
| `SKILL.md` | triggers, workflow spine, routing tables, truth ladder | on trigger |
| `references/` | 21 deep docs (styles, systems, engine surface) | per routing table |
| `workflows/` | 8 task playbooks (new project → release) | per task type |
| `project-profiles/` | per-project overlays (`riff-racers.md`, `*.example.md`) | only when named |
| `scripts/` | validators/auditors/build wrappers (stdlib bash+python) | at gate steps |
| `templates/` | performance report, import gate checklist | per delivery |
| `tests/` | structure + routing + script smoke tests | CI / before commit |

## Use

Install via the repo installer (`tools/install-skills.sh`, symlinks into
`~/.claude/skills` (Claude Code) + `~/.agents/skills` (Codex); oh-my-pi
loads both roots). Then any Defold task in an agent session triggers it;
explicit invocation stays deterministic:

```text
Use the defold-development skill to add split-screen local co-op to this
top-down shooter (Defold 1.14.1, Lua), with camera proxies and a focus plan.
Use the defold-development skill: implement save games with versioned schema
migration for this roguelike, non-destructive on old saves.
```

Deep docs load only on demand (progressive disclosure); `USAGE.md` carries
the full host guide.

Self-check:

```bash
python3 scripts/validate_skill.py            # structure + links + no genre defaults
python3 tests/test_skill.py                  # incl. 6 activation scenarios
python3 scripts/check_version.py             # baseline vs official releases
python3 scripts/audit_defold_project.py <dir>   # read-only project audit
python3 scripts/gltf_preflight.py <file.glb>    # import preflight
bash    scripts/bob_build.sh                      # dry-run; prints exact bob.jar command
```

## Maintaining

Engine updates: follow the routine in
`references/version-compatibility.md` — read release notes, re-verify gated
claims, never auto-migrate game projects. Blender-side modeling is delegated
to the optional `lowpoly-reference-to-blender` skill; this skill owns only
Defold-side integration and imports, and works fully without it.
