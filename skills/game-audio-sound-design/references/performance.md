# Audio performance engineering

Budgets are **project-specific** — templates/audio-budget.json is a starting
shape, not law. Measure on the platform, not on the dev box.

## Knobs (verified engine surface)

| Engine | voice cap | streaming | preload | priority |
|---|---|---|---|---|
| Defold 1.14.1 | `game.project [audio] max_sound_instances` (audit reads it) | `.sound stream: true` (ogg/wav long) | small wav components | none native — limit SFX count + cull distant |
| Godot 4.7.2 | per-player pool; bus count | OggVorbis `stream: true` on import | `ResourceLoader` preload short wav | playback priority via pooling + `max_polyphony` |

## Budget model (defaults illustrative)

```json
{"profile":"desktop","max_simultaneous_voices":48,
 "audio_memory_budget_mb":128,"stream_music":true,"preload_short_sfx":true}
```
Web/mobile: 16–24 voices, music streamed, sfx ≤2 s wav 44.1k mono.
Console/PC: pool 32–64 sfx, music streamed, short sfx preloaded.

## Rules (measure → change → re-measure)

- voice count spike sources: duplicate plays (audit finds double-refs),
  loops left running after scene change (engine adapter contract).
- memory: long files stream; loops bake short; rate/channels per budget —
  audit reports rate/channels mismatches as findings (`--budget` file).
- DSP: engine reverb/effects per-bus cheaper than per-source; no per-frame
  gain writes when static (cache).
- loader: manifest unreferenced-assets finding = candidate deletion list —
  review, never auto-delete.

## Offline measures

`audio_audit.py` (rate/channels/size vs budget, unreferenced),
`audio_batch.py report` (set inventory). Runtime cost = engine profiler,
platform device (documented limit: skill measures assets, engine measures
runtime — never both from here).
