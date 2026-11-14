# Scenes, Nodes, Resources, save data (4.7 baseline)

## Scene rules

- One root per reusable scene; scene = component when instantiated, level when
  booted. `PackedScene` files, never duplicated variants — exported vars and
  `@export var data: Resource` parameterize.
- `.tscn` text format (default) — diffable; keep in VCS with `.gd`, `.tres`,
  `project.godot`. `.import` sidecars: committed (4.x stores import settings there).
- Scene tree depth: shallow over clever; unique names (`%Name`) for anything
  scripted cross-scope.
- Nested `sub_resource` blocks in `.tscn` are fine for local shapes/materials;
  shared anything → external `.tres`.

## Resource discipline (data-driven gameplay)

```gdscript
class_name WeaponStats extends Resource
## Data-only; no node access, no side effects.

@export var damage: int = 10
@export var cooldown: float = 0.5
@export var sfx: Array[AudioStream] = []
```

- `.tres` files under `data/`: content tables, stats, theme configs, palettes.
- Load: `load("res://data/x.tres")` typed; `ResourceLoader.duplicate` semantics
  when instances must not share edits (resources are shared by reference).
- Custom Resources = the sanctioned "scriptable data" — no JSON schema layer
  unless content comes from outside the engine (then validate on import).

## Savegames (universal pattern)

- Serialize **plain dicts/arrays** → `FileAccess.open(path, WRITE/READ)` +
  `store_var`/`get_var` (binary) or `JSON.stringify` (debuggable). Version the
  payload: `{"version": 2, ...}`; migrate forward on load.
- Paths: `user://` only; per-slot/per-profile files; atomic write = write temp
  + rename (crash-safe).
- Never persist `NodePath`s into scenes that move; persist stable string IDs.
- Resources with script state: save the ID + fields, rebuild on load.

```gdscript
func save(path: String, payload: Dictionary) -> Error:
    payload["version"] = SAVE_VERSION
    var f := FileAccess.open(path + ".tmp", FileAccess.WRITE)
    if f == null: return FileAccess.get_open_error()
    f.store_var(payload)
    f.flush()
    DirAccess.copy_absolute(path + ".tmp", path)  # atomic-ish replace
    return OK
```

## Configuration truth-sources

| Layer | Lives in | Notes |
|---|---|---|
| Engine/project settings | `project.godot` | version-controlled |
| Per-developer | `*.override.cfg` | not committed decisions doc'd |
| Player settings | `user://` | versioned, validated on load |
| Content data | `.tres` | editor-visible, typed |

## Scene validation gates

- `godot --headless --import` reports broken deps; audit script greps
  `ext_resource`/`sub_resource` paths + script classes.
- Missing-script errors and orphan `res://` links surface at import; treat
  non-zero import log errors as build failures.
