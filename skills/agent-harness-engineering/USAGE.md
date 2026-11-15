# Using `agent-harness-engineering` in your agents

Same content as the README section in the repo root (canonical there); mirrored
into the symlinked folder for agents browsing locally.

## Claude Code

Read from `~/.claude/skills/agent-harness-engineering/`; triggers on harness
asks ("audit the agent harness", "fix retry loops", "optimize tool calls"):

```
Use agent-harness-engineering: audit this repo's agent harness, show the
score + findings, and dry-run the fix plan. No writes without approval.
```

## Codex

Via `~/.agents/skills/agent-harness-engineering/`:

```
Use agent-harness-engineering: benchmark tool_calls and error rate before vs
after the tool-granularity change; offline numbers stay labeled offline.
```

## oh-my-pi / other hosts

Name the skill + task; the scripts run anywhere python3 ≥ 3.10 exists.
Platform capability questions (permissions, traces, slash commands) follow
references/platform-adapters.md — verified-or-documented, never assumed.

## Entry points

SKILL.md (router) · scripts/*.py (CLIs; `--help` everywhere) · schemas/ ·
references/ (load on demand) · examples/ · tests/test_skill.py.
