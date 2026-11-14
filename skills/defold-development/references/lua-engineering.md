# Lua Engineering for Defold

Defold embeds Lua 5.1 (with project-selected 5.4 where configured — check
`game.project` `[script]` before using newer syntax; default builds remain
5.1-compatible). Idiomatic, boring, inspectable Lua wins.

## Script lifecycle (`.script` components)

```lua
function init(self)      -- once; build state, subscribe messages
function final(self)     -- teardown; unsubscribe where engine won't
function update(self, dt)-- frame; dt is real frame delta — scale physics!
function fixed_update(self, dt) -- engine fixed step (physics cadence)
function on_input(self, action_id, action)
function on_message(self, message_id, message, sender)
```

- Callbacks exist at file top level in `.script` files (the engine injects
  the environment); **modules** you `require` never define them.
- `init` must not depend on sibling GO init order — exchange via messages.
- Heavy init budget: build tables from data, don't `require` feature code you
  only touch later (lazy-require per scene is fine, per-frame is not).

## Style contract

```lua
-- module: one table, explicit returns
local Race = {}
Race.__index = Race

local DEFAULT_LAPS = 3

function Race.new(cfg)
    assert(cfg.track, "Race.new requires cfg.track")
    return setmetatable({laps = cfg.laps or DEFAULT_LAPS, t = 0}, Race)
end
```

- `local` everything; module-level constants `UPPER`. No `_G` pollution.
- Errors for programmer mistakes (`assert` on missing cfg), messages for
  gameplay events. Never `error()` per frame in hot paths.
- No class hierarchy depth > 2. Metatables where behavior is shared;
  plain tables + functions where it isn't. Artificial base classes are
  rejected.
- Comments only for invariants ("order matters", "why fixed step"), never
  line-by-line narration.

## Tables & memory

- Preallocate: `table.create` equivalent is fixed-size local tables or
  `table.insert`-free construction (`{x=0,y=0}`). Reuse scratch vectors:
  `vmath.vmath.vector3()` allocation per frame in 12 racers × 60 fps is
  measurable — keep module-level scratch or per-owner scratch.
- String keys static (`m.lap` not `m["lap"..i]` in loops).
- Clear caches in `final`; Defold recycles the script env, not your tables.

## Messages & addresses

```lua
msg.post("race:main:kart_1#script", "kart_input", {throttle = 0.5})
local id = hash("kart_input")   -- hash once, store; rehashing per frame is waste
```

- Build URLs once (init), store, reuse. `msg.url()` components over string
  concat.
- `on_message`: dispatch table `local HANDLERS = {[hash("a")]=f,...}`, single
  `elseif` chain acceptable; unknown id → single-shot log.
- Responses via `sender` when request/response semantics.

## Determinism (for rewind/replay — see rewind-simulation.md)

- Same input order → same output: fixed timestep in `fixed_update`, no
  `os.clock()`/frame-delta in simulation state, no `pairs()` order dependence
  for gameplay iteration (store an ordered key list).
- `math.random`: seedable — wrap it (`local rng = make_rng(seed)`) and log
  seeds into replay; `math.random` global state breaks replays.
- Float math is fine when step order is fixed; document tolerance for
  positions restored after rewind.

## Error handling

- `pcall` around data parsing (saves, JSON from disk) → fallback state + log.
- Log format: `sys.print`/`print` with `[module] what/why`; project log tag
  convention from existing code.
- Fail-fast in dev (assert), degrade in release only where the game must
  survive (user save corruption).

## Review pass (before commit)

- [ ] No new globals; no `require` in per-frame paths
- [ ] Lifecycle callbacks only in `.script` files
- [ ] Message ids hashed and centralized; URLs cached
- [ ] dt-scaled movement or fixed_update, never both for the same state
- [ ] Saves parse defensively; determinism notes where replay matters
