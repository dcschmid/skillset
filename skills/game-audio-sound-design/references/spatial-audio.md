# Spatial audio

Baseline fact: neither shipped engine gives you a full native 3D API set at
our verified versions — treat "spatial" as a *computed* layer unless the
project's engine version proves otherwise (check before claiming).

| Feature | Defold 1.14.1 | Godot 4.7.2 |
|---|---|---|
| 2D panning | `sound.set_pan` (−1..1, CP) | Player2D `max_distance`/panning |
| 3D positional | no source API — compute pan+gain in Lua | Player3D + listener (camera/AudioListener3D) |
| distance model | manual falloff formula (adapter: 6 dB/dist unit, tune) | `AudioStreamPlayer3D` unit_db + doppler opts |
| occlusion/reverb | none — extension/manual | occlusion via raycast + volume, Reverb buses |
| multi-listener / split-screen | fallback below | fallback below (one listener/viewport type) |

## Computed fallback (both engines, adapter emits this)

listener-relative `(x,z)` → pan = x/|d|, gain = base − k·log or −k·d
(document k). Update per frame for movers; freeze for static emitters.

## Split-screen / 2 players

Engines expose one listener per viewport type. Options, in order of boring:
1. shared "action center" listener (coop friendly, cheapest)
2. per-player mix priority: only nearest N sounds per player; UI sounds
   global (no duplicate UI voices)
3. second viewport + own bus tree (Godot) — heavier, test budgets
Never double-play a positional sound for two listeners without a rule for
which one the player hears where.

## QA (per engine adapter)

listener follows camera on scene change · no duplicate voices in co-op ·
pause keeps positions · critical gameplay cues survive distance (min-gain
clamp) · AUDIO_REVIEW_REQUIRED for direction readability.
