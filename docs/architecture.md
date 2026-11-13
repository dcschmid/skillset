# Architecture

## Delivery model

```
skillset (git, source of truth)
 ├── skills/<name>/ ──symlink──> ~/.claude/skills/<name>   (Claude Code)
 │                └──symlink──> ~/.agents/skills/<name>   (Codex)
 ├── profiles/<project>.md      loaded only when named by an invocation
 ├── tools/                     installer, uninstaller, installer tests
 └── docs/                      this guide, adding-new-skills.md
```

Symlinks mean one edit updates both agents. The installer
(`tools/install-skills.sh`) maintains `.installed-manifest`; the uninstaller
trusts only that manifest.

## Skill anatomy (progressive disclosure)

| Layer | Content | Loaded |
|---|---|---|
| SKILL.md frontmatter | name, description | discovery/trigger |
| SKILL.md body | workflow, gates, parameters, API notes | on invocation |
| references/*.md | domain depth (faces, karts, topology, export) | when the step needs it |
| scripts/*.py | working tools: detect, inspect, validate, render, export, verify | at the gate steps |
| assets/* | report templates | per delivery |
| tests/* | reproducible validation | CI / before commit |

SKILL.md stays a router; depth lives one hop away.

## Profiles

`profiles/*.md` are overlays (polygon budgets, priorities, engine targets).
A base skill must behave identically with no profile; a profile changes
numbers and emphasis, never the gates. This keeps Riff Racers specifics out
of unrelated projects.

## Skill independence

No cross-skill imports; no shared runtime beyond the host (Blender, agents).
A skill is copied/versioned/tested alone. Shared knowledge that earns reuse
gets promoted to a reference doc inside each consumer or a future shared
reference directory — not premature abstraction.

## Test strategy

1. Technical gates are automated and deterministic (E2E pipeline inside
   Blender background mode; installer behavior tests).
2. Visual fidelity gates are comparison-based (multi-view renders vs
   reference); score = observation or `VISUAL_REVIEW_REQUIRED`.
3. Both results ship in the quality report — never mixed, never one claiming
   the other.
