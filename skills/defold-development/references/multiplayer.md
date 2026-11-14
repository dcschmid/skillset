# Multiplayer, Split-Screen & Replay — Defold 1.14.1 baseline

Load for local multiplayer, split-screen, replay/rewind, or any online
question. Online netcode is **not** an engine feature — this file says what
is built and what you assemble. Determinism basics: `lua-engineering.md`.

## Local multiplayer (same machine, several humans)

Shipped: per-controller input. `action.gamepad` (number) identifies the
origin controller on every gamepad action; `connected`/`disconnected` actions
fire per controller; `raw` gives unfiltered buttons/axes/hats;
`action.gamepad_unknown` flags unmapped devices
(`/manuals/input-gamepads/`). HTML5 uses the browser Gamepad API (iframe
needs `allow="gamepad"`).

Shape: one input router → per-player state.

```lua
-- router (boot script on_input): player index from gamepad id
local PLAYER_BY_GAMEPAD = {}                    -- 0-based ids from engine
function on_input(self, action_id, action)
    if action.gamepad then
        local p = PLAYER_BY_GAMEPAD[action.gamepad]
        if p then msg.post(p.url, "player_input", {id = action_id, a = action}) end
    end
end
-- hot-join: on "connected" → assign next free slot, spawn via factory
-- leave:  on "disconnected" → park state, despawn avatar, free slot
```

Rules: player state owner = that player's GO; router owns the gamepad→player
table only. Keyboard sharing (WASD vs arrows) is the same router with
`action_id` splits. HUD: see `ui-ux.md` (per-player GUI sections or one GUI
with per-player nodes — no second GUI world unless scissored).

## Split-screen (the real mechanism)

No component toggle exists. Split = render script work: per viewport call
`render.set_viewport(x, y, w, h)` + `render.set_scissor` (or equivalent per
`/ref/render/`) with one camera + one draw pass each, drawing the same or
separate render targets (`/manuals/render`). Cost ≈ N× scene draw cost —
budget at `performance.md`. Alternative for co-op that never splits: shared
camera with zoom-out. Multiple `camera` components + acquire/release work
for *sequential* views (menus, cutscenes), not simultaneous panes.

## Online: NOT provided by engine

There is no lobby, replication, prediction, or session service in the engine.
Building blocks that ship: `socket` (LuaSocket TCP/UDP, `/ref/socket/`),
`http` (`/ref/http/`, `/manuals/http-requests/`), and extensions
(WebSocket, Photon Fusion/Realtime — extensions, verify maintenance status).
Everything else — protocol, authority, reconciliation — is yours.

Analysis checklist before writing a line:

| Question | Why it decides architecture |
|---|---|
| Players must affect each other live? | yes → client-server or host; no → independent sims + exchange |
| Tolerance for lag? | action game → prediction+reconciliation; turn-based → request/response over `http` suffices |
| Server language? | engine has no server runtime — Node/Go/whatever you host; `socket` is client-side |
| State size? | tiny (scores) → periodic sync; big world → delta compression needed |
| Rejoin/reconnect? | server persists state → session ids, snapshot restore (same serializer as saves) |

Server-authoritative default: client sends inputs, server simulates,
broadcasts state; clients interpolate. Client prediction (replay local input,
rollback on server correction) only when latency is felt — it doubles
testing cost. Never start with P2P.

Cheap honest ladder: 1) `http` + polling (leaderboards, async turns);
2) `socket` TCP + your own framing (small real-time); 3) WebSocket extension;
4) full netcode extension; 5) external server lib. Stop at the first rung
that plays right.

## Replay / rewind (offline, single-player)

Shipped pieces: `fixed_update`, `render.set_fixed_frame_interval`-style
stepping per `/manuals/`, `hash`-free ordered inputs. The recorder is yours:

```lua
-- Snapshot ringbuffer: fixed-capacity preallocated table, index wraps.
local CAP, ring, i = 600, {}, 1                        -- 10 s @ 60 Hz
for s = 1, CAP do ring[s] = {x = 0, y = 0, t = 0} end  -- slots reused, no GC
local function push(st)
    local slot = ring[i]; slot.x, slot.y, slot.t = st.x, st.y, st.t
    i = i % CAP + 1
end
-- record: fixed_update copies {pos=…, vel=…, hp=…, rng=seed_state}
-- rewind: pop newest → go.set_position, physics.set_velocity, restore rng
```

Requirements: fixed timestep sim (`fixed_update` only writes), every recorded
field is plain data (no vectors stored by reference — copy components), RNG
state logged (seed + call count, `lua-engineering.md`), playback re-drives
`fixed_update` not `update`. Rewind ≠ inverse transforms — it's restore from
capture. Budget memory: state size × rate × window; measure in profiler.

## Load order & gotchas

- Gamepad ids arrive 0-based; keep the player-slot table server-of-truth for
  local play.
- Collection-proxy boundaries cut physics worlds — split-screen players in
  one world must share a collection (`physics-ai.md`).
- HTML5: gamepads depend on browser support; feature-detect
  (`navigator.getGamepads` via `html5.run`).
- Replay files are version-tagged like saves (`architecture.md`): engine
  upgrades change float stepping; old replays may drift.
