# Profile: Riff Racers

Optional overlay for the Riff Racers project (loaded only when
`target_project=riff-racers`). The base skill stays project-independent.

## Project identity

- Game: Riff Racers — stylized low-poly racing, music theme
- Engine: **Defold** · Modeling: Blender (5.3 MCP live)
- 12 individual drivers + 12 individual karts
- Modular track/environment kit

## Style contract

- Deliberately stylized low-poly: strong readable silhouettes, clean facets,
  purposeful bevels, hard edges where the design says facet
- Faces are priority-critical: `face-modeling.md` passes run in full for every
  driver; identity preservation over speed
- Color/material: consistent palette per driver, palette locked to that
  driver's reference art

## Performance target (iGPU / weak systems)

| Asset | Polygon budget (tris) | Draw materials |
|---|---:|---|
| Driver character | 2500–4000 | ≤ 4 |
| Face region | ≤ 1200 (inside character budget) | — |
| Kart | 1500–3000 | ≤ 6 |
| Track module | ≤ 1500 | ≤ 4, shared atlas |
| Small prop | ≤ 300 | shared |

Scene frame budget: 12 karts + 12 drivers + track must stay under
~150k tris total, ~40 draw calls on integrated graphics.

## Quality gates (project override)

- Final drivers and karts: **≥ 90/100** visual score required
- Multi-View Blueprint Gate mandatory: drivers front/side/back; karts
  front/side/back/top
- Animated parts (wheels, steering) keep clean pivots; per-driver animations
  are a documented later workflow, not shipped half-bound

## Delivery

- `assets/<driver>.blend` + `<driver>.glb`, `assets/<kart>.blend/.glb`
- Quality report per driver and kart from `quality-report-template.md`
- Reference art is authoritative; missing views reconstructed and flagged

## Do not

- No fixed universal poly limits beyond this table
- No second Blender install, no system-wide Blender changes
- No external generation services (TripoSR/Local-3D-Forge lineage stays out)
