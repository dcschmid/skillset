# Project Profile Template: Voxel Survival — worked example

TEMPLATE. Copy → rename → fill. Demonstrates a profile for a project with
heavy runtime systems; also demonstrates honest feasibility notes (see
references/voxel-development.md — dynamic voxel worlds are NOT Defold
built-in; this profile records the extension/mesh-generation decision made
for THIS project only).

## Project identity

- Game: <name> — voxel survival, single player, editable terrain
- Engine: Defold 1.14.1 Stable · Voxel source: <MagicaVoxel/generator>
- Scope gates: no online multiplayer, no high-poly pipeline.

## Feasibility decision (recorded, not silently assumed)

- Terrain edits at runtime require generated meshes or a native extension —
  chosen path: ______; effort estimate: ______.
- Static voxel props: mesh export (glTF) — standard import gate.

## Engine feature surface

| Need | Defold path |
|---|---|
| Chunk streaming | own Lua/native chunk manager + async asset load |
| Collision for edited terrain | generated collision shapes |
| Save | versioned chunk-diff serialization |

## Performance budget (measure; do not ship unmeasured)

- Chunk size ______; active chunks ______; target 60 fps on ______.
- Texture: single voxel atlas, ______ px, one material per chunk mesh.

## Quality gates

- Edit→remesh latency under ______ ms (RUNTIME level).
- No visible seams between chunks (VISUAL level).
