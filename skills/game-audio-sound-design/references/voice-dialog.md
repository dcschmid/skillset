# Voice & dialog (optional pipeline)

Backend has NO TTS — do not claim it. Voice arrives by import or a separate
TTS integration behind the same gates.

## Pipeline

import VO files → `audio_validate.py --profile voice` (loudness band,
clipping, dc) → loudness-match to project voice target (bands: −20..−8 RMS
guidance) → bus: VOICE separate from MUSIC/SFX (adapter emits routing) →
dialog files ↔ subtitle table mapping (project format; manifest notes field
carries the link) → localization: per-language assets as separate manifest
entries (same asset_id + locale suffix), same loudness spec so mixes survive
translation.

## Constraints

- never assume TTS from game-audio-forge; never ship third-party voices
  without rights/consent (license_status stays review_required until
  documented)
- ducking music under VO = engine bus automation (adaptive-music.md), not
  baked processing on the VO file
- validation: same gate as sfx; intelligibility check is AUDIO_REVIEW_REQUIRED
  against the music bed at final levels
