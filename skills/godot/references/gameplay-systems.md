# Gameplay systems (universal shapes, 4.7 baseline)

Genre-agnostic building blocks. Instantiate only what the detected genre needs;
a puzzle game does not ship an inventory, a visual novel does not ship pathfinding.

## Input abstraction

- Define semantic actions in Project Input Map (`move_left`, `jump`, `interact`),
  never raw keys in gameplay code: `Input.is_action_pressed("jump")`,
  `_unhandled_input(event): if event.is_action_pressed("jump")`.
- Controllers/keyboard/mouse/touch all fold into the same actions; deadzones on
  `Input.get_joy_axis`; rebind UI edits the saved InputMap, not code.
- UI vs gameplay input: `Control` consumes first; world input in
  `_unhandled_input`. Split-screen: per-player `InputEvent` `device` filter.

## Character controllers

- 2D: `CharacterBody2D.move_and_slide()`; gravity from
  `Vector2(0, project_setting gravity) * delta`; coyote time/jump buffer as
  timers in the mover, not per-game hacks.
- 3D: `CharacterBody3D`; rotation vs velocity direction as an exported toggle
  (top-down vs platformer vs RPG all differ — same class).
- Vehicle/object motion: `RigidBody3D` + forces, or `VehicleBody3D`; do not
  kinematic-emulate physics bodies that physics was chosen for.

## State machines

```gdscript
enum State { IDLE, RUN, JUMP, FALL, ACTIONS }
var _state: State = State.IDLE
func _transition(to: State) -> void:
    if _state == to: return
    _exit_state(_state); _state = to; _enter_state(_state)
```

`match _state` in `_physics_process`. States as nodes ONLY when states own
scenes/animations heavy enough to justify a tree; generic FSM addons: reject
until 3+ consumers prove it.

## Event / signal architecture

Entity signals upward (`died`, `collected`), managers listen, bus
(`autoload` EventBus with typed `RefCounted` event classes) only cross-cutting
(quest system hearing "any enemy died"). Connect once in `_ready`, disconnect
implicit on free.

## Abilities & cooldowns

Ability = `Resource` (data: cost, cooldown, visuals) + component (runtime:
timer, targetability). Cooldown via accumulated `delta`, pause-safe
(`get_tree().paused` freezes `_process`, timers keep unless `PROCESS_MODE`).

## Interaction

`Area2D/3D` detector + collision layer "interactable"; owner emits
`interactable_hovered/unhovered`; player forwards to UI. Raycast alternative for
"look at" targeting — pick per camera style (top-down areas, FPS raycast).

## Inventory / quests / dialogue (request-gated)

Same pattern each time: typed `Resource` data + `RefCounted` runtime +
signals; storage `Dictionary[id -> count/state]`; persistence via the
savegame pattern (`scenes-and-resources.md`). Dialogue: `class_name` line
`RefCounted`s or a plugin (Dialogic etc.) only when branching volume justifies
a dependency — evaluate compatibility per `references/godot-versions.md`.

## Level & progression management

Level = scene with typed metadata `Resource`; `LevelFlow` autoload/scene
orchestrates load/unload with threaded loading; progression = versioned save
dict. Checkpoint = serializable snapshot, not scene duplication.

## Spawning & pooling

`SceneTree` groups (`add_to_group("enemies")`) for queries; pooled
instantiate/free for high-churn (bullets); `MultiMeshInstance` for visuals
mass; factories hold `PackedScene` + count budget.

## AI (gameplay-side; nav-side in navigation-and-ai.md)

`EnemyAI` component with `enum` behavior states + timers; perception =
`VisibleOnScreenNotifier`/raycast/`Area`; no ML by default.

## Pause & time

`get_tree().paused = true` + `PROCESS_MODE_ALWAYS` UI; time-scale for
slow-mo (rhythm games drive mechanics off `Engine.time_scale`-scaled
timers consistently — test both).
