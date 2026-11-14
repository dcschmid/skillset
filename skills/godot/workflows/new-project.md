# Workflow: New Godot Project

No project exists (or only stubs). Output: bootable, version-pinned skeleton
with honest scope notes. No genre/style defaults leak in.

## Steps

1. **Capture inputs** — idea, genre?, art style?, 2D/2.5D/3D?, platforms?,
   team?, size horizon?. Unknowns → smallest reversible assumption, written
   into the project README. Ask ONLY when a wrong guess is expensive
   (e.g. C# vs GDScript with a codebase promise).
2. **Version pin** — engine = current stable per
   `references/godot-versions.md` (4.7.2) unless user pins another; record
   version+channel in README + `config/features` comes free from editor saves.
3. **Derive architecture from needs** — one yes/no per system: physics?
   multiplayer? savegames? UI scale? (`references/architecture.md` decision
   table). Systems not asked for are NOT scaffolded.
4. **Renderer + style gate** — renderer from platform floor
   (`3d-development.md`); pixel → nearest/stretch/integer settings
   (`pixel-art.md`); voxel → data model decision (`voxel-art.md`);
   Blender only if assets come from Blender (`blender-integration.md`).
5. **Layout** — `references/architecture.md` baseline tree; prototypes =
   `main/ + scripts/ + assets/`. Commit `project.godot` immediately.
6. **Minimal boot** — main scene, one gameplay component script, input actions
   in Input Map, collision layer names if physics — nothing else.
   `examples/base-project/` is the shape reference.
7. **Verify** — `scripts/headless_check.sh <dir>`: STATIC parse →
   `--headless --import` → `--quit-after` boot. No engine on host → emit the
   commands as UNVERIFIED, never fake a pass.
8. **Document** — README: pin, chosen systems, deferred systems, run/build/
   test commands.

## Anti-rules

No `framework/` layer beside the engine; no inventory/quest/race manager
unless the genre asked; no addon install "for later"; no engine upgrades,
no Blender dependency, no Low-Poly assumption, no second `.gitignore` truth —
the existing repo conventions win.
