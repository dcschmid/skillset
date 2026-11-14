# Project Architecture (Defold)

Read the project before proposing structure. This is the shape of Defold
projects and the decisions that keep them maintainable.

## Runtime unit model

```
Collection (scene)            main.collection is the boot scene
 └─ Game Objects              GOs: position + component list + id
     └─ Components            script, sprite, model, collision, sound,
                              label, factory, proxy, particlefx, mesh...
```

- **Collection Proxy** = async scene load/unload boundary. Post
  `proxy_loaded` handling; init the child collection's boot message before
  enabling (`collection_proxy` + `msg.post("#proxy", "init")` flow per
  `/manuals/collections/`).
- **Factory** = runtime GO instantiation (`factory.create()`). Pool through
  it; don't create/destroy every frame.
- **Component extensions** (`*.script_api` / `component` extensions) exist
  for reusable typed behavior; reach for one only when the same component
  logic appears 3+ times — else a plain Lua module is cheaper.

## Module layout (conventions seen across healthy projects)

```
game/
  main/            boot collection + boot scripts
  modules/         feature modules (race, ui, audio, ai, save, input)
  shared/          pure Lua libs (no engine state): math, fsm, ringbuffer
assets/            imported models/textures (read-only after import)
```

Adjust to the project's actual tree; never impose a second layout.

## Lua module pattern (used everywhere, see lua-best-practices)

```lua
-- game/shared/fsm.lua
local M = {}
function M.new(spec) return setmetatable({spec = spec, state = spec.initial}, {__index = M}) end
function M:transition(event) ... end
return M
```

`require` paths follow project root; modules return one table; no globals
except the engine-mandated script lifecycle callbacks in `.script` files.

## Messaging

- `msg.post(url, message_id, message)` — URLs address
  `socket:collection:go:component`. Prefer **component-relative** `"#comp"`
  and parent paths; store URLs, don't rebuild strings per frame.
- One owner per state. If the race director owns lap state, UI *subscribes*;
  it never keeps its own copy of the truth.
- Broadcast events: tag with a project message-table (`game/shared/messages.lua`
  constants) so greppability survives; Defold allows custom string ids —
  centralize them.
- `on_message` dispatch on `message_id`; unknown ids → log once, return.

## Scene flow / loading

1. `main.collection` boots, loads config, shows splash.
2. Proxy per scene (track, garage, menus). Flow: load proxy → child sends
   ready → parent enables → old scene unloads.
3. Cross-scene state travels via: (a) explicit params on proxy init, or
   (b) a small `session` module (Lua state) — never via file I/O in the hot
   path.
4. Preload via proxy's child + async resource loading; a hitch during race
   start is an architecture bug.

## Save / persistence

- `/manuals/save-games`-documented storage for small persistent data.
- Bigger saves: serialize to a project-defined format
  (`json.encode`/`lua.json` per `/ref/json`) written to application-specific
  save dir; version-tag saves (`{version=1,...}`) with an additive migration
  ladder. Never `load()` untrusted strings at runtime.

## State machines & events

- FSM as pure Lua (testable without engine). Transitions log
  `from→event→to`; illegal transitions assert in debug, log-and-ignore in
  release.
- Event bus: module-local subscriber list + `msg.post` fanout only when the
  subscriber is an engine object. No stringly-typed global event soup.

## Data-driven systems

Track/car/driver definitions live in `.project`-adjacent data: Lua tables
compiled from CSV/JSON at edit time, or engine resource files
(`*.collection`, `.model`, `.material`). Runtime code reads data; it doesn't
embed per-driver `if` ladders.

## Checklist before any architecture change

- [ ] Existing module found and extended, not duplicated
- [ ] State ownership named (who writes, who reads)
- [ ] Load/unload path still single-owner per scene
- [ ] Save format versioned if touched
- [ ] No new globals; no parallel conventions
