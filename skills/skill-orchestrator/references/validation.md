# Validation rules and tiers

Four tiers, never conflated. A finding carries `tier` + `severity`
(`error|warn|info`); profiles decide which tiers can produce which
severity for which field.

| Tier | Source | Example |
|---|---|---|
| standard | open spec (agentskills.io/specification) | `name`/`description` required, name ≤64 lowercase-hyphen, description ≤1024, compatibility ≤500, metadata = string map |
| host | host extensions | `allowed-tools` (Claude; experimental in standard) |
| repo | skillset AGENTS.md | `name == directory`, SKILL.md ≤500 lines, scripts compile |
| unknown | not in any registry | e.g. `homepage:` → `warn`, tier `unknown`, NOT a standard failure |

## Profiles

- `portable` — standard rules only; host keys are `info`, never errors.
- `claude` — standard + Claude Code extensions accepted natively.
- `codex` — standard + Codex host metadata; repo conventions still apply.

Switch: `--profile portable|claude|codex` (default `portable`).

## Frontmatter checks (deterministic)

| Check | Tier | Severity |
|---|---|---|
| meta.yaml (unclosed fence / bad YAML / non-mapping) | standard | error |
| meta.name.required / length / format | standard | error |
| meta.name.dirmatch | repo | error |
| meta.description.required / length | standard | error |
| content.activation (no trigger phrasing in description) | repo | warn |
| meta.compatibility.length | standard | error |
| meta.metadata.shape / meta.allowed-tools.shape | standard | warn |
| host.allowed-tools | host | info |
| meta.unknown-field | unknown | warn |

## Structure / content checks

`structure.broken-link` (error) — relative Markdown link target missing.
`structure.orphan-reference` (info) — references/ file never linked.
`size.body` (warn) — body over 500 lines breaks progressive disclosure.
`scripts.syntax` (error) — scripts/ Python must compile.
`content.*` — activation section, negative examples, PASS/FAIL gates
(repo authoring rules from AGENTS.md/docs/adding-new-skills.md).

## Skills-discovered-not-invented

Discovery walks `**/SKILL.md`. Facts recorded: dir, frontmatter, body
size, files, cross-mentions, git last-modified. Anything the files cannot
answer stays `unchecked` — scoring credits 0 for it, never full marks.

## skills-ref interop

If the official `skills-ref` validator is installed, its report can be
piped as an extra lane; all core checks above run locally without it so
the system never hard-depends on external tooling.