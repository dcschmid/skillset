# Routing engine

Task text → auditable plan. Deterministic scoring; a model may refine a
plan but plans must stand without one. `route`/`plan` never mutate —
they answer "which skills, why, in what order" and stop.

## Signals (in scoring order)

1. **Explicit selection** (`--skill X`) — score 100, always in.
2. **Tech named in task** (astro, react, godot, defold, blender…) — +30.
3. **Domain tokens** (accessibility, security, testing, seo, i18n,
   design, writing, 3d-assets, game, web) — +15 per mapped skill.
4. **Skill id literally in task** — +25.
5. **Graph dependencies** of selected skills — pulled in as `dependency`.

Threshold: ≥10 to be considered; primary ≥25; support ≥15; cap 8
(precision over coverage — selection is never "everything enabled").

## Exclusion rules (verified against repo conventions)

- Engine exclusivity: godot ↔ defold-development — naming one suppresses
  the other (AGENTS.md: skills stay independent; one engine per project).
- Framework respect: react/next project never triggers astro migration;
  naming one web framework suppresses the rival unless both are named.
- Web-domain skills (seo-performance) do not hijack game tasks:
  "Optimiere ein Godot-Spiel" routes to godot only.
- A skill's declared scope wins: `accessibility` owns a11y across all
  frameworks; framework skills own framework specifics.

## Plan output

`selected` (skill, score, role, reason), `considered_rejected`
(skill + why — near misses are part of the audit trail),
`execution_order` (primary first, then layer order
coordinate → implementation → asset → audit → verification → content),
`quality_gates` (only gates relevant to the selection),
`expected_results`.

## Integration mechanism (documented limit)

A skill cannot force other agents to load it. Invocation is through real,
supported surfaces: SKILL.md `description` triggers (Claude Code/Codex
discovery), explicit "Use <skill> to …" phrasing, and per-project
AGENTS.md/CLAUDE.md pointers. The orchestrator writes plans — the host
agent executes them with its own skills.