# Mixing & mastering (game, not album)

Bus model (concept — engines differ): MASTER ← MUSIC · SFX · UI · VOICE ·
AMBIENCE · CINEMATICS. Engine adapter creates buses; this layer sets levels.

## Measured facts available OFFLINE (ffmpeg astats, verified)

peak dBFS · RMS dBFS · flat factor · DC offset · duration/rate/channels
(via `audio_common.measure/probe`, consumed by audit/validate).

**LUFS/EBU R128 is NOT measurable offline here** (loudnorm is single-pass,
streaming). Report `lufs: NOT_TESTED`; measure at playback with the engine's
meter or `ffmpeg ebur128` during a monitored play session — documented, not
faked. Targets (guidance, per project): SFX transient-led, RMS bands per
profile in `audio_validate.py`; music −20..−8 RMS; voice intelligible over
music by ≥4 dB spectral pocket.

## Per-category targets (configure, never universal)

| Bus | rms guidance | notes |
|---|---|---|
| ui-sfx | −24..−10 | short, never fatigues |
| gameplay-sfx | −20..−6 | informs gameplay, priority above ambience |
| ambience | −30..−16 | bed, low variance |
| music | −20..−8 | duck under voice via bus gain (engine), not baked |
| voice | −20..−8 | clarity first |
| cinematics | −22..−10 | wider range ok |

## Pipeline (per asset)

trim silence → fade edges → level to band (normalize/limit) →
rate/channels per budget → profile validate (peak/silence/dc/loudness) →
bus routing in engine. Ducking: engine bus gain automation (Defold
`set_group_gain` ramp / Godot bus volume), never baked compression between
categories.

## Mastering a set (not a track)

Loudness parity within category (±3 dB audit finding), no cumulative
clipping on master bus (sum headroom: N concurrent sfx × peak ≤ 0 dBFS →
budget in performance.md), AUDIO_REVIEW_REQUIRED for balance judgement.
