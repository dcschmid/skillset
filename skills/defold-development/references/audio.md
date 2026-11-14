# Audio — Defold 1.14.1 baseline

Load for SFX, music, mixing questions, or music-driven mechanics. Facts from
`/manuals/sound`, `/manuals/sound-streaming`, `/ref/sound-lua` (verified
against the generated API listing for this baseline). FMOD is an **asset/
extension** (`/assets/fmod/`), not the engine mixer.

## What ships

- **Sound component** on GOs; `.sound` resource (wav/ogg). Play via
  `msg.post("#sound", "play_sound", {...})` or `sound.play("#sound", props)`
  → returns `play_id` (≤32 simultaneous voices per component).
- **Per-voice/per-component control** (all verified `/ref/sound`):
  `sound.set_gain(url, g[, {play_id=…}])`, `sound.set_pan(url, p)`
  (−1..1, constant-power), `sound.pause`, `sound.stop(url, {play_id})`,
  `speed` property (0–50×). Gain linear 0–1; dB = 20·log10(gain).
- **Completion**: `sound_done` / `sound_stopped` messages (or
  `complete_function` callback on `sound.play`) — carry `play_id`. Drive
  sequences from these, not timers guessing durations.
- **Mixer groups**: flat group tree under `master` —
  `sound.set_group_gain("soundfx", g)` (gain [0..1] → [0..−60 dB]),
  `sound.get_groups()`, `sound.get_group_gain`, plus metering
  `sound.get_peak(group, window)`, `sound.get_rms(group, window)`.
- **Streaming**: `/manuals/sound-streaming` for long music tracks (loop points
  documented there); `.sound` on small SFX. Streaming ≠ sample-accurate
  scheduling across tracks.
- Mobile niceties: `sound.is_music_playing()`, `sound.is_phone_call_active()`
  (non-mobile → always false).

## What does NOT ship (honest list)

| Want | Engine status | Path |
|---|---|---|
| FMOD-style bus graph, sends, sidechain | no (groups are flat gains) | FMOD extension asset, or Lua mixing |
| FX (reverb/chorus/…), ducking | no | manual: Lua fades via `set_group_gain` ramps; extension |
| 3D positional audio API | **no listener/source functions in `/ref/sound-lua` for this baseline** (earlier-era `sound.set_listener`/`set_source`: UNVERIFIED here — check before use) | compute `pan`+gain from relative position yourself (below) |
| Master bus compression/limiting | no | mix assets to target loudness; final `set_group_gain("master", g)` |

Positional by hand (this is the shipped-primitive answer):

```lua
-- owner of player pos runs this per tick; d = distance falloff
local d = vmath.length(other_pos - player_pos)
local gain = math.max(0, 1 - d / self.audio_range)
local side = vmath.dot(right_vec, (other_pos - player_pos):normalize())
sound.set_pan(url, side * gain)          -- pan encodes ±45°, constant-power
sound.set_gain(url, gain * self.master)
```

Manual mixing discipline: N group gains written at most a few times/sec
(lerp in `update` if smooth needed); meters via `get_rms` to auto-level —
that's a limiter you own, test it.

## Latency notes

Mixing runs on its own thread (visible as `Sound` in Remotery frame profiler).
Latency is device/driver-bound, not tunable from Lua: no buffer-size API in
this baseline's `/ref/sound`. Keep SFX short and preloaded; hitch-free
first-play requires the sound loaded (component exists; don't
`resource.set_sound` swap in the hit moment). HTML5: browser audio stack adds
its own latency; test rhythm games on target browsers.

## Music-driven mechanics

Clock from playback position, not `os.clock`: record start timestamp, then
`t = (now − t0) * speed`; with `speed` changes, re-anchor `t0`. Event map =
sorted beat table `{ {t=1.25, fn="spawn"}, … }`; `update` advances a cursor
and fires passed events once. `sound_done` on the track closes the loop.
Sample-accurate? No — frame-quantized (≈16 ms at 60 fps): fine for platform
hops, not for a strict rhythm title without input-latency calibration you own.

```lua
function update(self, dt)                      -- clock = audio position
    self.t = self.t + dt * self.speed
    while self.cursor < #BEATS and BEATS[self.cursor + 1].t <= self.t do
        self.cursor = self.cursor + 1; fire(BEATS[self.cursor])  -- ordered keys
    end
end
```

## Budgets & ownership

SFX = mono wav/short ogg; music = streamed ogg. Voice cap 32/component —
cull by distance/gain in your own spawner (above pattern doubles as culling).
Loudness: normalize authored assets (target −14 LUFS-ish by meter with
`get_rms` on the master group during QA, not by runtime FX).
