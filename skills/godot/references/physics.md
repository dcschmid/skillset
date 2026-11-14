# Physics (4.7 baseline)

## Engine selection (project setting `physics/...`)

- 2D: single classic 2D engine (GodotPhysics). No 2D Jolt in 4.7 line (verify).
- 3D: GodotPhysics (default, Bullet-lineage legacy) **or** Jolt
  (`physics/3d/engine = "JoltPhysics3D"`, built-in since 4.4+, hardened in the
  4.7 era). Jolt = determinism + stability for vehicles/ragdolls/stacks; verify
  the pin via docs page before committing the project.
- Pick once, per project. Switching engines mid-project changes every
  tuning constant (mass, gravity, solver iterations) — treat as engine upgrade.

## Node roles (any genre)

`StaticBody3D` environment; `RigidBody3D` thrown/vehicle/ragdoll;
`CharacterBody3D` kinematic characters; `Area3D` triggers/regions;
`Generic6DOFJoint`/`Hinge`/`Pin` for mechanical links; `SoftBody3D` per
version support (verify). Collision layers/masks planned in project settings
before first scene.

## Raycast & queries

`PhysicsDirectSpaceState3D.intersect_ray` / shape queries for aim, ground
checks, LOS; `PhysicsServer3D` for bulk; `Area` overlap for cheap many.
Fixed-step: physics in `_physics_process` only; `physics_ticks_per_second`
project-wide constant before tuning.

## Determinism & replays (racing/sim genres want this)

Fixed timestep + seeded RNG + snapshot state (`get_physics_process_delta`
cadence); Jolt favored for cross-run stability. Verify determinism claims on
target build, not editor.

## Gates

STATIC: layer mask table documented; RUNTIME: no tunneling at max speed
(timestep vs velocity); profiler physics time within budget.
