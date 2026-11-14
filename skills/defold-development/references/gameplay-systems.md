# Gameplay Systems — Defold 1.14.1 baseline

Load when designing a gameplay feature. None of these systems ship unless the
project asks for them; each is an optional shape to adopt, resize, or skip.
State ownership rules and messaging patterns: `architecture.md`. Lua idioms and
determinism: `lua-engineering.md`.

Every shape below states: **use when** / **state owner** / **do NOT build first**.

## Player movement

Use when: any avatar controls something. Owner: the player GO's script.
Don't build first: a generic "entity framework".

```lua
-- dt-scaled (arcade, frame-coupled ok) — update(self, dt):
local v = go.get_position()
v.x = v.x + self.input.x * self.speed * dt   -- input arrives via on_input
go.set_position(v)                            -- reused vector where hot

-- Physics-driven: apply forces in fixed_update(self, dt), never both paths
-- for the same state. Collision character-controller pattern: physics-ai.md.
```

## Input abstraction

Use when: >1 device (kb/mouse, gamepad, touch) or rebindable controls.
Owner: one boot-time module mapping raw `action_id` → semantic game events.
Don't build first: per-feature `on_input` ladders scattered across scripts.

```lua
-- game/shared/input_map.lua — translate once, broadcast semantics
local EVENTS = {[hash("move_left")]  = "walk", [hash("jump")] = "jump"}
function M.route(action_id, action)          -- called from on_input
    local e = EVENTS[action_id]
    if e then M.emit(e, action) end          -- players keyed by action.gamepad
end                                          -- (multiplayer.md)
```

## Collision / physics handling

Use when: gameplay reads contacts. Owner: physics owns simulation; gameplay
owns response. Don't build first: a "collision manager" god-object. Shape,
groups, message flow, and filter strategy: `physics-ai.md`.

## Enemy / NPC template

Use when: 2+ NPCs share perceiving/deciding/acting structure. Owner: each NPC
instance owns its state; director owns spawn/waves. Don't build first: an
inheritance tree. Composition: `fsm + senses + mover` tables on one GO script.

```lua
local Mover  = require("shared.mover")       -- waypoint/A* path follower
local Fsm    = require("shared.fsm")         -- see FSM below
function init(self)
    self.fsm   = Fsm.new(NPC_SPEC[self.kind])-- data, not subclassing
    self.mover = Mover.new(self.lane)
end
function fixed_update(self, dt)
    self.fsm:tick(self, dt)                  -- transitions post go.move_to
end
```

## FSM

Use when: discrete states with legal-transition rules (idle/patrol/chase,
menu open/close, dialogue step). Owner: the thing that changes behavior.
Pure Lua module — testable headless (`architecture.md`). Never a base class.

```lua
local fsm = Fsm.new({initial="idle", events={
  idle  = {spot="chase"},
  chase = {lose="patrol", reach="attack"},
}})
fsm:fire("spot")   -- logs from→event→to; illegal: assert(debug)/log(rel)
```

## AI + navigation

Defold 1.14.1 ships **no native navmesh** — not in the manuals, not in the
Lua API list. Mark any "navmesh" claim UNVERIFIED. Shipped options:
waypoint lists, Lua A* on a grid/graph (`physics-ai.md`), steering math
(`vmath`). Detour-based navmesh exists only as community native extensions.

## Inventory / equipment

Use when: items persist across scenes. Owner: a session/Lua module
(`architecture.md` session), NOT a scene script. Data: item definitions in
data files, runtime tables hold `{id, count}` only. Don't build first:
world-space item physics or an "item class hierarchy".

```lua
-- inventory.add(id, n) — id is a string key into items.lua
local inv = require("modules.inventory")
inv.add("key_blue", 1)                        -- validates, emits "item_added"
```

## Quests / dialogue

Quest = tagged progress flags + objectives table, owned by a `progress`
module; dialogue = data (Lua/JSON lines + branch ids) rendered by GUI, state
in a small FSM. Don't build first: a visual editor or scripting DSL. Keep
branching as `id → {lines, next}` tables; grep survives, DSLs rot.

## Skills / abilities

Ability = data (`cooldown`, `cost`, `effect`) + one executor function per
effect kind. Owner: the ability module checks cost, spends, applies. Don't
build first: an ability-graph node editor. Timer use `timer` module
(`/ref/timer`), cancel in `final`.

## Health / damage

Damage is a message `{amount, source, kind}`; target clamps, applies rules,
re-emits `died`. Owner: entity owns hp; UI subscribes. Don't build first: a
global combat resolver. Numbers live in data files.

```lua
msg.post(self.target, "damage", {amount = dmg, kind = hash("fire")})
-- on_message: hp = math.max(0, hp - msg.amount) — if hp==0 → post "died"
```

## Checkpoints / respawn

Checkpoint = serialized snapshot handle (see save/load) written by a trigger;
respawn = restore + camera cut owned by scene director. Don't build first:
dual-state undo systems (that's rewind — `multiplayer.md`).

## Save / load

Follows `architecture.md`: small → `sys.save`/`sys.load`; big →
`json.encode` to save dir; version-tag + migration ladder. Checkpoints reuse
the same serializer — one format, not two.

## Economy

Currency = integers in the session module; transactions are functions that
validate + log. Prices in data files. Don't build first: floating-point money
or an inventory-coupled shop engine. Persist through save/load only.

## Procedural hooks

Seed everything; log seeds with the save (`lua-engineering.md`). Generation
lives in pure modules taking `(seed, params)` — never `math.random` globals.
Chunk/streaming detail: `procedural-generation.md`.

## Camera rigs

Camera component + `/ref/camera` acquire/release. Rig = Lua module computing a
target transform each `update`, feeding `go.set_position`/`look_at`. Owner:
one camera per view; split-screen = render-level, `multiplayer.md`. Don't
build first: a camera *manager* — post the focus request to the camera.

## Interaction systems

Raycast/trigger → "use" event → responder GO handles (`on_message`). Reach
test shipped via `physics.cast_ray`. Don't build first: an interactable
registry with priorities before the game needs >3 interactable types.

## Animation state machines

Engine side: flipbook/model animations (`/manuals/animation`). Gameplay side:
reuse the FSM module; animation is a *reaction* to state, never its owner.
Blend/transition data in the animation, timing in data files.

## Game rules / progression

Rule set = pure Lua reducer `(state, event) → state'` (round time, score, win
conditions) owned by a director script; UI and audio subscribe to emitted
events. Progression = flags table in the session module. Don't build first: a
rules DSL or ECS. Reducers are unit-testable (`debugging-testing.md`).

## Selection order (avoid premature frameworks)

1. One GO + one script with inline logic.
2. Extract a pure Lua module when the logic gets tested or reused (2 uses).
3. Extract a data file when values change without code review.
4. Only then: component/template shapes. Kill any abstraction with <2 users.
