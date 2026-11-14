# Physics & NPC AI — Defold 1.14.1 baseline

Load when touching simulation, contacts, or NPC movement. Engine-side facts
verified against `/manuals/physics` and `/ref/physics`, `/ref/b2d`,
`/ref/bullet3d`. Gameplay responses: `gameplay-systems.md`.

## Engine choice (2D vs 3D)

| Need | Engine | Selected where |
|---|---|---|
| 2D | Box2D (legacy, default) **or** Box2D v3 (opt-in) | App Manifest → Physics 2D; `None` strips 2D physics |
| 3D | Bullet | App Manifest / platform config |

Box2D v2 vs v3 changes simulation results — retune per-version settings in
`game.project [physics]` after switching. Component workflow + `physics`
module work with both; not every low-level `b2d.*` function exists in both —
check the generated API page per function. Mixing 2D and 3D simulation in one
collection is not a thing: pick per collection, per axis of gameplay.

## Units & stepping

1 unit = 1 meter; tuned for moving objects 0.1–10 m. Scale with
`[physics] scale` (e.g. `0.02` → 200 px = 4 m) and raise gravity to match.
Stable sim: `[physics] use_fixed_timestep = 1`; cadence from
`[engine] fixed_update_frequency`; drive bodies from `fixed_update(self, dt)`.
Each top-level collection = separate physics world; no contacts or ray hits
across collection-proxy boundaries.

## Collision object stack

- **Components**: `collisionobject` with shape list (primitive or compound;
  2D polygon/box/circle, 3D box/sphere/capsule…). Static/kinematic/dynamic.
  `/manuals/physics-objects`, `/manuals/physics-shapes`.
- **Groups/filters**: every object in a named group; collision pairs declared
  in `.project` `[physics]` — this is the real filter layer.
  `/manuals/physics-groups`. Script-side group tables for the functional APIs.
- **Contact flow**: `contact_point_response` (solid hits, gives world pos,
  normal, relative velocity, mass) and `collision_response` (triggers,
  sender list) arrive in `on_message` on both GOs.
  `/manuals/physics-messages`, `/manuals/physics-resolving-collisions`.
- **Event listener**: `physics.set_collision_listener`-style global hook —
  existence confirmed only via `/manuals/physics-events`; verify exact name
  against `/ref/physics/` before use (UNVERIFIED spelling).

## Ray casts

`/manuals/physics-ray-casts`: linear probes against the collection world —
ground checks, line-of-sight, aim assist. Shipped entry points are
`physics.cast_ray` (sync) and async variant; exact signatures/return fields
live in `/ref/physics/` — verify, don't recall. Filter by group table.
Ray casts are per-world (see collection boundary note above).

## Joints & constraints

Component-level: declared in `.collision` files between collision objects.
Low-level (Box2D legacy): `b2d.joint` create/destroy; Bullet:
`bullet3d.constraint` (`/ref/b2d.joint`, `/ref/bullet3d.constraint`). Joints
are simulation, not gameplay: doors/ropes/vehicles use them; character
follow-cams do not.

## Functional worlds (headless sim)

`b2d.world` / `bullet3d.world` give engine-owned worlds you drive from Lua —
useful for physics puzzles in a UI, deterministic minigames, replays. Heavier
API surface; adopt only when the component workflow can't express the need.

## Character controller (none built-in)

Defold ships **no** CharacterController component. Standard shapes:

1. **Dynamic body + locked rotation** — box/capsule body, `set_rotation`
   frozen; move via forces/velocity in `fixed_update`; grounded via short
   downward ray or stored contact count. Simplest; inherits solver quirks.
2. **Kinematic body + `go.set_world_position` steps** — you own the step
   machine (horizontal → snap-down → wall probe). Full control, more code.
3. **No physics** — pure transform movement + ray probes for walls
   (`gameplay-systems.md` movement). Fine for arcade/grid games.

Pick by how much solver behavior you want. Never mix: one path per body.

## Determinism (replay/rewind consumers)

Fixed timestep ON, `fixed_update` for all sim writes, ordered iteration (no
`pairs` order for gameplay), logged seeds (`lua-engineering.md` Determinism).
Box2D/Bullet are deterministic for identical step+input order on one build;
across Box2D v2↔v3 or engine upgrades, replays may drift — version-tag replay
files. Snapshot/rewind buffer pattern: `multiplayer.md`.

## NPC navigation — what is and isn't shipped

**Shipped:** none of the navmesh kind. No `/manuals/` page, no Lua namespace.
Any "Defold navmesh" = community extension (Detour ports on the asset portal)
— extension, not engine. Mark UNVERIFIED otherwise.

**Do it yourself, boring and testable:**

```lua
-- Waypoints: data-driven loop of vmath.vector3; advance on distance check.
-- A* on a grid: pure Lua, grid from tilemap at load, path = {i,j} list.
local path = astar.find(grid, start_cell, goal_cell)  -- pure module, unit-testable
-- Follow: pop waypoint when |pos - wp| < r; steer = (wp - pos):normalize()
```

| Shape | Cost | Use when |
|---|---|---|
| Waypoints | trivial | authored routes, trains, patrols |
| Grid A* (Lua) | ~100 LOC + tests | tile/tilemap worlds |
| Graph A* (nodes+edges Lua) | ~150 LOC | point-to-point 3D |
| Steering (seek/flee/arrive) | ~50 LOC | smooth local motion |
| Detour extension | dependency | true poly-navmesh; verify maintenance |

Rules: nav data is *data* (files), not code; queries rate-limited (per-NPC
interval, not per frame); path invalidation on level edits is a data bug you
must test. Grids from tilemap layers beat hand-typed obstacles.
