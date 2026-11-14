# Multiplayer & local co-op (4.7 baseline)

Implement ONLY when the project asks; scope = the smallest mode that satisfies
it (couch co-op ≠ client-server internet).

## Mode ladder

1. **Split-screen/local co-op**: one `SceneTree`, multiple `Camera`s/`Viewport`s
   or rect-split; no networking layer at all; input = `device` filtering.
2. **LAN/server-host**: `MultiplayerAPI` via `ENetMultiplayerPeer`;
   server-authoritative or listen-server.
3. **Online**: dedicated or listen + relay later; high-level = RPC +
   `MultiplayerSpawner`/`MultiplayerSynchronizer`; low-level = custom packets.

## High-level pattern (verify node names per version)

`SceneMultiplayer` root; `MultiplayerSpawner` per replicated container;
`MultiplayerSynchronizer` per entity (properties + method sync); `@rpc` calls
with explicit `authority`/`call_local`/`reliable` modes. Server-authoritative:
clients predict movement, reconcile from authoritative snapshots.

## Latency & feel

Interpolate remote entities (buffer + `Engine.get_physics_interpolation`);
dead-reckon player locally; lag compensation scoped to genre (shooters ≠ RPGs).

## Gates

RUNTIME both peers headless (`--remote-debug`/two instances); AUTOTEST:
join→spawn→sync→disconnect matrix; VISUAL desync review at 100–200 ms delay.

## Web export

WebSocket vs ENet per web export target: verify per version (web = WebSocket,
ENet unavailable — confirm in docs before promising browser multiplayer).
