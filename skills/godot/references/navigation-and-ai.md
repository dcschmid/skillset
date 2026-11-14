# Navigation & AI (4.7 baseline)

## Navigation server stack (any genre needing pathing)

`NavigationRegion2D/3D` + baked `NavigationPolygon`/`NavigationMesh`;
`NavigationAgent2D/3D` on movers; `NavigationPath2D/3D` for display/debug.
Bake static geometry; runtime `NavigationObstacle` for dynamic blockers;
 avoidance = `NavigationAgent` avoidance callbacks.

## When to use what

- Grid/tile tactics: A* on data grid (own code or `AStarGrid2D`) — NOT nav mesh.
- Character locomotion: `NavigationAgent3D` + corridor following.
- Flight/swimming: 3D nav mesh with agent radius/height per species.
- RTS hordes: navmesh + avoidance OFF past profile threshold (costlier).
- 2D top-down: `NavigationRegion2D` from scene polygons.

## AI behavior layer

`EnemyAI` script: `enum` states (patrol/chase/attack/flee/return) + timers;
perception via `Area`/raycast/`VisibleOnScreenNotifier2D`; group queries
(`get_tree().call_group`) for "any target". Behavior-tree addons ONLY when
states exceed ~6 and branching is data-driven (compatibility gate).

## Gates

RUNTIME: pathing across bake seam sanity; no agent stuck loops over baked
region; debug nav overlay via `--debug-navigation`.
