# Compatibility profiles and hosts

## Profiles

| Profile | Standard | Host extensions | Repo conventions |
|---|---|---|---|
| `portable` | enforced | reported `info`, never errors | enforced |
| `claude` | enforced | Claude Code fields native | enforced |
| `codex` | enforced | Codex metadata native | enforced |

Rule: a field valid for one host is NEVER a general skill error. Unknown
fields → tier `unknown`, severity `warn` — portability note, not failure.

## Field disposition table

| Field | standard | claude | codex |
|---|---|---|---|
| name, description | required | required | required |
| license, compatibility, metadata | optional | optional | optional |
| allowed-tools | optional (experimental) | native | native |
| anything else | unknown-tier warn | warn unless registered | warn unless registered |

## This repository's verified state (last probe 2026-11-14)

- 13 collection skills: `name`+`description` only.
- `human-writing`: adds `license`, `metadata`, `compatibility` — all
  standard-optional; clean under every profile.
- No skill currently uses host-only fields → `portable` is the honest
  default profile; `claude`/`codex` matter once host fields appear.
- Known genuine standard findings: several descriptions exceed the
  1024-char standard limit (reported as blocker-class errors, not hidden).

## Hosts

- Claude Code: reads SKILL.md frontmatter; skills symlinked under
  `~/.claude/skills` (this repo's installer).
- Codex: reads SKILL.md; `agents/openai.yaml` supported alongside —
  the orchestrator skill ships one; other skills do not need it.
- Open-standard hosts (agentskills.io clients): portable profile is the
  contract.

## skills-ref (official validator)

Optional extra lane. If `skills-ref` is on PATH, run it as a second
opinion; core checks are local by design so no external tool is required
for any command to complete.