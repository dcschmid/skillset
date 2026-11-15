# Adaptive / interactive music

States (examples — project defines truth): MENU · EXPLORATION · TENSION ·
COMBAT · HIGH_INTENSITY · BOSS · VICTORY · DEFEAT · PAUSED. Techniques:
horizontal resequencing, vertical layering, stingers, intensity ramps.

## Architecture that works on both shipped engines

Engine-agnostic director (Lua/GDScript via engine_* adapter emit):
- one music bus/channel per layer; state machine decides target state;
- transitions: instant | crossfade (bus gain ramp) | bar-locked (queue at
  next bar via playback position) — engines give play position, you schedule;
- pause: engine pause freezes playback (Godot `stream_paused`, Defold
  component pause) — document per engine; never leave orphan streams.

Verified limits (never promise native):
- Defold 1.14.1: no listener API, no native ducking/bus FX — gain ramps via
  `sound.set_group_gain`; bar-sync by reading play position in update().
- Godot 4.7.2: `AudioStreamPlayer.stream_paused`, bus volume/` AudioServer`;
  one listener per viewport type (2D/3D) — multi-listener needs extra
  Viewports/audio buses.

## Transition contract (every state change)

1. fade-out current (bus or player gain, 0.2–1.5 s or bar-aligned)
2. start next at deterministic grid point (measured BPM, see
   music-production.md — never metadata BPM)
3. stop finished layers exactly once (no double music)
4. verify: no click (loop seam checked), no double play, volume returns
   on resume, scene-change keeps or cleanly stops music.

## Fallback ladder

crossfade → cut with stinger → single adaptive-less track + filter. Prefer
fewer moving parts that measure clean over ambitious graphs that click.

## QA

`audio_audit.py` per state file (seam, loudness parity ±3 dB between states)
+ scripted listening checklist per transition (AUDIO_REVIEW_REQUIRED):
clicks, double-play, pause/resume, scene change, restart.
