# Audio (4.7 baseline)

## Architecture (genre-agnostic)

Buses in Project Settings (Master ← Music/SFX/Ambience/UI/VO); players:
`AudioStreamPlayer` (screen), `AudioStreamPlayer2D/3D` (positional,
attenuation curves per style). Streams: OGG music (loop points), short WAV
SFX (verify format support per version).

## Systems

- **SFX**: pool of players per bus, `PlaybackOptions` pitch variance;
  polyphony caps from profiler.
- **Music**: crossfade between `AudioStream`s via two players + tweened volume;
  loop offsets for stems; sync-to-gameplay via `get_playback_position` —
  rhythm mechanics: audio clock authoritative over `TIME`.
- **Buses**: effects per bus (reverb zones via `Area` + `AudioServer` bus
  swaps), volume persistence through savegame settings.

## Web/mobile

Web export audio latency + codec constraints per version docs; mobile sample
rate settings; verify on the LOWEST target during the runtime gate.

## Gates

RUNTIME: no `AudioServer` under-runs in log at max entity load; VISUAL(auditory):
levels meter peaks −1 dBFS; music loop seam inaudible.
