# Project Profile: Riff Racers — opt-only overlay

Loaded ONLY when the invocation names `riff-racers`. Everything here is
project truth for one game; none of it is a Defold default, and none of it
(racing, karts, drivers, rewind, split-screen) applies to other projects.
Base skill workflow and gates stay unchanged.

## Project identity

- Game: Riff Racers — stylized low-poly racing, music theme
- Engine: Defold (baseline 1.14.1 Stable) · Modeling: Blender 5.3 (MCP live)
- 12 individual drivers + 12 individual karts
- Modular track/environment kit

## Engine feature surface this project uses (rationale for future maintainers)

| Need | Defold path | Status |
|---|---|---|
| Local multiplayer split-screen | render script scissor/multiple viewports | implemented in render script |
| Rewind | fixed-step snapshots + ringbuffer | own Lua module, not engine feature |
| Multiple HUDs | per-player GUI instances | standard GUI |
| Gamepad-per-player | input bindings + per-player action handling | standard input |
| Low-poly karts/drivers | glTF 2.0 GLB import | import-time gate |

## Style contract

- Deliberately stylized low-poly: readable silhouettes, clean facets,
  purposeful bevels, hard edges where the design says facet.
- Faces are priority-critical: face-modeling passes run in full for every
  driver; identity preservation over speed.
- Palette locked per driver to that driver's reference art.

## Performance targets (iGPU / weak systems — project numbers)

| Asset | Polygon budget (tris) | Draw materials |
|---|---:|---|
| Driver character | 2500–4000 | ≤ 4 |
| Face region | ≤ 1200 (inside character budget) | — |
| Kart | 1500–3000 | ≤ 6 |
| Track module | ≤ 1500 | ≤ 4, shared atlas |
| Small prop | ≤ 300 | shared |

Scene frame budget: 12 karts + 12 drivers + track under ~150k tris total,
~40 draw calls on integrated graphics.

## Quality gates (project override)

- Final drivers and karts: ≥ 90/100 visual score required.
- Multi-view blueprint gate mandatory: drivers front/side/back; karts
  front/side/back/top.
- Animated parts (wheels, steering) keep clean pivots; per-driver animations
  are a documented later workflow, not shipped half-bound.

## Delivery

- `assets/<driver>.blend` + `<driver>.glb`, `assets/<kart>.blend/.glb`
- Quality report per driver and kart from the skill's
  `templates/performance-report.md` / quality template.
- Reference art is authoritative; missing views reconstructed and flagged.

## Do not (project scope)

- No fixed universal poly limits beyond this table for other projects.
- No second Blender install, no system-wide Blender changes.
- No external generation services (TripoSR/Local-3D-Forge lineage stays out).
