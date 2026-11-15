# Sound design workflow (any genre/engine)

Categories (extend freely): UI/menu, gameplay feedback, character actions,
foley/steps, vehicles/engines, weapons, impacts, magic, sci-fi, weather,
ambience, nature, creatures, objects, cinematics, transitions, win/lose.

## Loop (12 steps — gate at 7 and 11)

1. situation → 2. sound function (inform? feedback? atmosphere?) →
3. character spec (pitch band, transient, length, loops?) →
4. search existing assets FIRST (manifest, `audio_audit.py` facts) →
5. layered gaf prompt (`gaf sfx "short description, character, material,
space" --duration S`) → 6. variants: 2–4 seeds or `gain/atempo` ops →
7. **technical gate**: `audio_validate.py --profile <profile>` — kill
   silent/clipped/wrong-format; untested ≠ passed →
8. cull → 9. process (`audio_process.py`: fade/normalize/resample;
   originals stay) → 10. export format for target engine/platform →
11. **manifest**: `audio_manifest.py` (prompt/seed/license/measured) →
12. integrate via engine adapter, playtest in situ.

## Variation without regeneration

Round-robin pool: N variants + light `gain ±1..2 dB`, `atempo 0.97..1.03`
(audio_process ops) — never for gameplay-critical timing cues where pitch
carries information (engine RPM readouts etc.). Defold: retrigger component
with different `gain`; Godot: `pitch_scale` on pooled players.

## Processing map (ffmpeg-verified ops only)

| Want | op | note |
|---|---|---|
| de-click loops | fade / loop-xfade | 10 ms edges, see audio_process |
| level to target | normalize | peak dBFS; loudness band per profile in validate |
| length/time | atempo 0.5–2.0 | pitch preserved |
| space | none native here | engine reverb zones or bake in generation prompt |
| pitch | resample ≠ pitch; use engine pitch_shift/player pitch | document |
| silence | trim (silenceremove) | shortens SFX attack gaps |

EQ/compression/filtering/reverb exist as ffmpeg filters but bake quality
loss risk → propose (`--dry-run`), user approves, then apply + re-measure.

## Acceptance (every asset)

readable · duration sane · rate/channels per budget · no clipping ·
not silent · profile loudness band · provenance recorded · license status
set · **manual listening: AUDIO_REVIEW_REQUIRED** (separate state, never
merged with measurements).
