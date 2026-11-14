# godot — universal Godot game-development skill

Agent skill for building ANY Godot 4.x game with coding agents (Claude Code,
Codex): any genre, any art style (pixel, voxel, low-poly, high-poly, stylized,
realistic, hybrid 2.5D), any project size. Engine baseline pinned and
version-gated: **Godot 4.7.2 stable** (`ed1daf0b`, 2026-08-18).

Host invocation — install with `tools/install-skills.sh godot` (symlinks
into `~/.claude/skills` for Claude Code, `~/.agents/skills` for Codex;
oh-my-pi loads both roots), then invoke by name:

```text
Use the godot skill to add coyote-time jumping to the player controller
(Godot 4.7, GDScript, static typing).
Use the godot skill to review my AnimationTree: signals fire twice on scene
reload — find the root cause and fix it with a regression test.
```

- Entry point: `SKILL.md` (routing tables → progressive disclosure)
- `references/` deep per-topic docs · `workflows/` ordered procedures ·
  `scripts/` runnable tooling · `examples/` minimal projects ·
  `tests/` STATIC validation

Non-destructive, version-honest: anything not verified on a real 4.7.2 engine
is reported UNVERIFIED, never faked. Blender is optional, genre defaults are
forbidden, existing project conventions always win.
