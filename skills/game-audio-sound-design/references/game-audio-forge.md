# backend truth (verified against the installed code, 2026-11)

## CLI contract (scripts/gaf — bash, config/gaf.json)

```
gaf music "PROMPT" [--bpm N] [--duration 10-600] [--seed N] [--steps N]
     [--cover SRC [--cover-strength F] [--noise-strength F]]
     [--repaint SRC --from S --to S] [--ref AUDIO]
gaf sfx "PROMPT" [--backend sa3|dasheng] [--duration N] [--steps N]
     [--cfg F] [--seed N]
gaf status | ui | help
```

- Output: `<root>/output/{music,sfx}/<ts>_<slug>.wav` + `.meta.json`
  sidecar (prompt/seed/params). Collisions → `-2`, `-3`; never overwrites.
- GPU queue: gaf waits while its generator processes run (pgrep on
  ace-lm/ace-synth/sa3-generate/dasheng-audiogen). Sequential by design
  (8 GB VRAM budget) — do not parallelize generations yourself.
- FFmpeg finalize only on real rate/format change (ffmpeg.target_rate=48000,
  enabled). sfx sa3 arrives 44.1 kHz stereo natively.

## Generators & measured behavior

| | music | sfx default | sfx legacy |
|---|---|---|---|
| stack | acestep.cpp ACE-Step 1.5 SFT DiT + 0.6B LM Q8 | sa3.cpp Stable Audio 3 small-sfx Q8 | audiogen.cpp Dasheng |
| format | 48 kHz stereo | 44.1 kHz stereo | 16 kHz mono |
| timing (RTX 5070) | 30 s ≈ 9 s / ~4.5 GB | 5 s ≈ 2 s / ~2.5 GB | ≈4 s / 1.8 GB |
| license | MIT everything — commercial OK | MIT runtime + Community weights (<$1M/yr) | runtime UNLICENSED — internal only |

Measured (docs/PROMPTING.md): `--bpm` is NOT executed by the DiT — tempo
comes from the caption words (epic ≈172, groove ≈106). Fixed seed ≈ stable
DiT, LM run random. `use_cot_caption=false` → verbatim caption, deterministic
but ~-20 dB quieter. lego/extract/complete (stems) need the base model —
unavailable with SFT/turbo.

## Prompting (the caption is a paragraph, not tags)

5 layers, in order: genre+core → riffs/instruments → production/era →
energy/structure → use-case/vibe. Tags → tempo roulette. Lyrics:
`[Instrumental]` = instrumental (wrapper sets it).

## Failure playbook (understandable → actionable)

| Symptom | Cause | Fix |
|---|---|---|
| `ace-lm not found` / `sa3-generate not found` | binaries not built | backend `bash scripts/setup.sh` |
| models dir missing | weights not downloaded | backend models.sh / hf download (SETUP.md §6) |
| hangs at "GPU busy" | another generator runs | wait; check `pgrep -f 'ace-|sa3-'` |
| nvcc/nvcc-not-found in shells | gaf-env not sourced | `source scripts/gaf-env` |
| output silent/quiet | cot/CoT or genre RMS | remeasure via audio_audit; regenerate layered prompt |
| config missing | repo not set up | re-create config/gaf.json from backend README |
