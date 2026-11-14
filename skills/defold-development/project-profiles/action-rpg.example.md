# Project Profile Template: Action-RPG — worked example

TEMPLATE. Copy → rename → fill. Shape for a systems-heavy 2D/2.5D project;
shows how gameplay systems from references/gameplay-systems.md get adopted
ONE AT A TIME with named state owners. Systems here are this project's, not
Defold defaults.

## Project identity

- Game: <name> — action-RPG, <2D top-down | 2.5D>, single player
- Engine: Defold 1.14.1 Stable · Art: <pixel | low-poly 3D>
- Scope gates: no split-screen, no voxel editing.

## Systems adopted (each with exactly one owner)

| System | Shape from | Owner module | Status |
|---|---|---|---|
| Movement | gameplay-systems.md | modules/move | |
| Health/damage | gameplay-systems.md | modules/combat | |
| Inventory | gameplay-systems.md | modules/inventory | |
| Dialogue | gameplay-systems.md | modules/dialogue | |
| Quests | gameplay-systems.md | modules/quests | |

Adoption order = gameplay order; nothing is scaffolded before it is needed.

## Data-driven rules

- Item/enemy/dialogue definitions in data tables (Lua/JSON compiled at edit
  time); runtime code contains no per-item `if` ladders.

## Save

- Version-tagged saves, additive migration ladder; corruption → pcall
  fallback + log (lua-engineering.md).

## Performance budget (starting point — measure)

- ≤ ______ active entities, ≤ ______ draw calls, 60 fps on ______.

## Quality gates

- Combat feel reviewed vs reference clip (VISUAL).
- Save/load round-trip identical for fixed input log (AUTOTEST).
