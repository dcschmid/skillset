# Architecture — universal Godot project shapes

Scale to the project: prototype (< 10 scenes), medium (10–100), large (100+).
Never scaffold for the next size up. Existing project layout wins.

## Baseline layout (any genre, any style)

```
res://
├── project.godot
├── main/                 # boot scene + scene-flow root (main.tscn)
├── scenes/               # gameplay scenes, folder-per-system, PascalCase .tscn
├── scripts/              # flat or mirrored per-system .gd (snake_case, class_name)
├── components/           # reusable node scripts (health, cooldown, fsm driver)
├── data/                 # .tres resources: stats, config, content tables
├── assets/               # art/audio imports (spritesheets, glb, ogg, ttf)
├── shaders/              # .gdshader + .gdshaderinc
├── ui/                   # Control scenes + theme .tres
└── addons/               # third-party, only if adopted deliberately
```

Small projects collapse to `main/ + scripts/ + assets/`. No `framework/`
directory beside the engine; Godot nodes ARE the framework.

## Decision table (drive from detected needs, never defaults)

| Need | Godot-native answer | Skip when |
|---|---|---|
| Shared state (score, settings, save) | autoload singleton (thin, typed) | feature is local → parent/child |
| Decoupled events | signal on the emitting node; EventBus autoload only cross-cutting | direct signal connect suffices |
| Per-entity behavior | child component nodes (`class_name FooComponent extends Node`) | one-off → inline script |
| Mode switching (idle/run/dead) | `enum` + `match` in owner, or state nodes if states are heavy | never a generic FSM addon by default |
| Data-driven content | custom `Resource` + `.tres` tables | tiny constants → `const` |
| Cross-scene comms | signals up, typed refs down; groups for "any of" | autoload getter fallback only |
| Pools (bullets, FX) | `Array` pool + `set_process(false)` / `visible` | pooling before profiling |

## Scene-flow patterns

- **Single-scene prototypes**: everything under one root — fine; refactor only
  when a second consumer appears.
- **Scene switching**: `get_tree().change_scene_to_file()` (prototypes) or a
  persistent root + add/remove children (games keeping audio/progress alive).
- **Level loading**: `ResourceLoader.load_threaded_request` /
  `get_threaded_load_status` loop with a progress UI (verify API in 4.7 docs).
- **PackedScene + instantiate** for spawnable entities; never duplicate scene
  files per variant — parameterize with exported `Resource`/vars.

## Component pattern (node-based composition)

```gdscript
class_name HealthComponent extends Node
## Attach under any Node that takes damage. Owner-agnostic.

@export var max_hp: int = 3
var hp: int:
    set(value):
        hp = clampi(value, 0, max_hp)
        if hp == 0: died.emit()
        else: health_changed.emit(hp, max_hp)

signal died
signal health_changed(current: int, maximum: int)

func _ready() -> void:
    hp = max_hp
```

Composition over inheritance: entity = scene tree of small typed components;
no deep `_Process` chains. Components emit signals; owners decide consequences.

## Autoload discipline

Max 3–6 autoloads; each one file, typed, documented, no gameplay logic —
state + accessors. Name `GameEvents`, `SaveManager`, `AudioDirector` style;
grep autoloads in `project.godot` before adding.

## Signals over polling

`connect` in `_ready` (or exported signal connections); `Callable` + bind over
string paths. Cross-cutting event bus ONLY when 3+ consumers exist, and it
still carries typed payloads via `class_name` event `RefCounted`s.

## GDScript vs C# selection

- GDScript default; C# when the team already writes C#/needs shared libs, and
  the export targets have mono builds (verify per version).
- Mixed projects: GDScript gameplay + C# systems is legal but doubles test
  surface — prefer one language per project.

## Refactoring triggers (large projects)

String paths → typed refs; autoload getters → injected `@export` nodes;
`.tres` growth → split per-domain; 500+ line script → component split. Refactor
on evidence, keep behavior identical, run the verification ladder after each.
