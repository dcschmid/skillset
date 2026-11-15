# Audio accessibility (skill boundary: audio-side only)

Cross-cutting a11y policy lives in the accessibility skill — this skill
implements the AUDIO surface, never a second a11y framework.

## Ship-list (both engines, adapter-supportable)

- separate volume sliders: MUSIC/SFX/UI/(VOICE/AMBIENCE) — engine bus/group
  gain (Defold groups via `set_group_gain`, Godot buses) persisted in save
- mono mixdown option (both engines: low-pass/merge at master; document
  platform route if native toggle exists)
- dynamic-range reduction: profile presets tighten loudness bands in
  `audio_validate.py` (raise floors, cap peaks ±)
- mute options + pause behaviour: adapters respect engine pause
- subtitles/sound captions + visual cues for critical audio: the GAME owns
  presentation; skill obligation = flag which sounds are information-bearing
  (manifest `notes`/category `gameplay-feedback`) so visuals can mirror them
- night mode / reduced loudness: re-validate at lowered target bands

## Validation hook

`audio_validate.py` bands are the machine-checkable half; the a11y checklist
(sliders exist, mono works, captions cover gameplay-critical cues) is
AUDIO_REVIEW_REQUIRED + a11y-skill audit for the cross-cutting half.
