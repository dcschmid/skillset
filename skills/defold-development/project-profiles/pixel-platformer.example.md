# Project Profile Template: Pixel Platformer — worked example

TEMPLATE, not a live project. Copy → rename → fill. Shows the expected shape
of a project profile so real profiles stay uniform. Nothing here is a Defold
default; the base skill behaves identically with zero profiles.

## Project identity

- Game: <name> — 2D pixel-art platformer, single player
- Engine: Defold 1.14.1 Stable · Art source: Aseprite/sheets
- Scope gates for THIS project: no 3D, no voxel, no online.

## Engine feature surface

| Need | Defold path | Notes |
|---|---|---|
| Character movement | own Lua FSM + dt-scaled velocity | coyote time, jump buffering |
| Levels | tilemap + tile source per world | hand-authored |
| Save | `sys.save` small tables / versioned JSON | check `/manuals/save-games/` size limit |
| Camera follow | script-driven GO camera, integer snap | see references/2d-pixel-art.md |

## Style contract (numbers belong HERE, not in the base skill)

- Base resolution 320×180 or 640×360, integer-scaled to fit window.
- Pixel grid 16×16 tiles; sprite pivot bottom-center.
- Nearest filtering on ALL pixel assets; atlas padding per skill checklist.

## Performance budget (starting point — measure to confirm)

- ≤ 80 draw calls target, ≤ <PROJECT CAP> MB texture memory.
- 60 fps on <target hardware>.

## Quality gates

- Shimmering check on all camera movement (VISUAL level).
- Input feel: jump arc reviewed against reference clip.

## Do not

- No generic-systems import from the base skill unless this project asks.
