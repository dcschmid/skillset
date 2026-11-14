# Agent integration & activation

## Activation mechanics (real mechanisms only, no invented hooks)

- **Claude Code / Codex / local models with skills support**: SKILL.md
  frontmatter `description` carries trigger phrases; agent selects by task
  match. Install via repo installer symlink (skillset convention) →
  `~/.claude/skills`, `~/.agents/skills`. Edits propagate live.
- **Auto-activation**: natural for write/rewrite/audit-prose tasks
  (README, blog, devlog, email, marketing, UX copy, story, release notes).
  Must NOT activate on pure code/config edits or rewrite existing prose
  unasked.
- **Codex**: reads skills from `~/.agents/skills`; invocation via task match
  or explicit `$human-writing`. No slash-command guarantee — document task
  phrasing instead.
- **Claude Code**: `/skill-name` availability depends on host version;
  portable path is always task phrasing ("use the human-writing skill").
- Local models without skill loading: paste SKILL.md + needed reference file.

## Capability honesty

- Python tools detect/plan/validate/apply-approved-diffs; the calling agent
  writes prose. Never present script output as the editorial step.
- Reports never assert authorship; scores count findings.
- URL-only analysis ≠ source rewrite; JS-hydrated text can be missed; then
  the report says extraction-limited.
- Site edits: dry-run default; writes only through approved patch spans.

## Skill collaboration table

| Partner | Theirs | Ours |
|---|---|---|
| astro / react-nextjs | structure, components, build | visible text inside |
| accessibility | semantics, a11y gate | phrasing inside a11y limits |
| design-authenticity (anti-AI-design) | visual sameness | textual sameness |
| godot / defold / blender tools | engine, assets | dialogue, lore, tutorials, release notes |
| future skills | their domain rules | prose layer, never overrides domain rules |

Conflict rule: domain skill owns the artifact; human-writing owns language
inside it. Both fire → each reports its own lane; user approves merges.
