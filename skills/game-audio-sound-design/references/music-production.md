# Music production (backend: ACE-Step 1.5 via gaf)

Types: menu, select, world/level themes, exploration, combat, boss, racing,
chase, horror, victory/defeat stingers, ambient beds, credits. Genres: any —
the model is genre-agnostic; your prompt vocabulary is the interface.

## Prompt recipe (measured, docs/PROMPTING.md)

Paragraph in 5 layers: genre+core / instruments / production era /
energy+structure / use-case. Add "instrumental" semantics via the wrapper's
`[Instrumental]` lyrics (default). `--duration 10..600`, `--seed` for
re-runs, `--steps` trade speed. `--bpm` does not steer the DiT — tempo lives
in the words (epic/speed ≈170, groove/stomp ≈105, thrash ≈115+).

## Technical verification (never trust metadata)

Generated metadata `bpm` is a wish. For rhythm-locked systems measure:
backend `python3 scripts/gaf-quality.py file.wav` → measured bpm +
confidence (>1.5 solid), rms, hf, stereo corr. Sync work: pick variant by
**measured** BPM, or normalize grid with `audio_process.py --op "atempo F"`.
Loop readiness: seam energy via `audio_audit.py` loop-seam-risk; crossfade
with `loop-xfade` op when it must loop.

## Multi-layer (vertical) material

Independently generated tracks are NOT stems: match measured BPM ±2 %,
length (trim to bars), tonal center (listen), and arrange so layers can enter
at bar lines. Generate bed + toppers with the same seed family + prompt
core, verify each, then document layer offsets in the manifest. If the game
needs true stems: the SFT/turbo model cannot (lego/extract need base model)
— say so, don't fake.

## Delivery gate per track

profile `music` loudness band · loop seam checked when looping · duration in
spec · provenance + license (`approved`: ACE-Step MIT) · AUDIO_REVIEW_REQUIRED
for musical impact (separate state).
