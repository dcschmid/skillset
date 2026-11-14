# GDScript & C# engineering (4.7 baseline)

Language claims verified against https://docs.godotengine.org/en/4.7/tutorials/scripting/gdscript/.
Existing project style beats everything here.

## GDScript style spine

- **Static typing everywhere public**: `var speed: float = 240.0`,
  `func jump(v: Vector2) -> void:`. Untyped `var`/args only for local
  throwaways; never on exported API.
- `class_name` on reusable scripts; file name = class name (snake_case file,
  PascalCase class per Godot convention for `class_name` scripts).
- Annotations: `@export` (inspector data), `@onready` (node refs),
  `@tool` (editor scripts only), `@rpc("any_peer", "call_local")` for network.
- Doc comments `##` on classes and public methods → appear in tooltips/help.
- `enum` + `match` over string state; `const` tables over if-chains.

```gdscript
class_name PlayerMover extends CharacterBody2D
## Genre-agnostic kinematic mover: caller supplies velocity intent.

@export var acceleration: float = 1_200.0
@export var friction: float = 1_600.0

func move(delta_intent: Vector2, delta: float) -> void:
    var target := delta_intent * max_speed
    velocity = velocity.lerp(target, 1.0 - exp(-friction * delta)) \
        if delta_intent == Vector2.ZERO else \
        velocity.move_toward(target, acceleration * delta)
    move_and_slide()
```

- Frame-rate independent motion: multiply by `delta`; `physics_process` for
  gameplay physics, `process` for visuals/UI interpolation.
- `await` for sequencing (`await get_tree().create_timer(t).timeout`, signal
  one-shots); no timers-with-callback spaghetti.
- Determinism where replay matters: seed `RandomNumberGenerator.new()`,
  fixed-step for simulation code.

## Node access & lifecycle

- Node paths: `$Name` / `@onready var hud: CanvasLayer = %Hud` — unique-name
  `%` refs over long paths; `get_node_or_null` only when optional.
- `_enter_tree` → `_ready` (children ready) → process → `_exit_tree`.
  Dependencies in `_ready`, never `preload`-cycle through scene files.
- `queue_free()`; guard loops with `is_node_ready()`/validity checks after await.

## Error handling

- `assert()` for programmer errors; runtime `push_error`/`push_warning` for
  data problems; never swallow with empty `_` branches silently.
- Resource loading: `ResourceLoader.exists` or `load()` null-check on optional
  content; hard deps can assert.

## C# (when the project chose it)

- Partial classes on nodes; `[Export]` fields; `[Signal]` delegates →
  `EmitSignal`. Same node lifecycle. Verify per-version mono export support
  before promising platforms (`references/export-and-release.md`).
- Mixed-language signals work; keep public boundaries typed.

## Typing gates for verification

`godot --headless --check-only --script path.gd` parses without running
(editor builds; extended flag set). In CI run it over every `.gd` before any
runtime check — fastest failure. `--check-only` alone does NOT prove imports of
scenes; combine with `--import`.

## Performance idioms (measured, not folklore)

- `StringName`/`&"name"` literals for repeated node names/signal names.
- Cache `@onready` refs; no `get_node` in hot loops.
- `Array`/`Dictionary` typed where possible (`Array[Enemy]`).
- `set_process(false)`/`set_physics_process(false)` when idle; visibility
  toggles over alpha-fade-when-off.
- Static `preload` for same-frame deps; runtime `load` for optional content.
