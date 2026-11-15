# Quality standards (reproducible QA)

Verdicts: PASS | WARNING | FAIL | NOT_TESTED — untested never PASS.
Creative/creative-adjacent judgement → `AUDIO_REVIEW_REQUIRED`, emitted as a
separate field; measurements never impersonate listening.

## Gate profiles (audio_validate.py)

| profile | checks |
|---|---|
| ui-sfx | readable, rate/channels, peak, silence, dc, loudness band, provenance |
| gameplay-sfx | + duration ≤ spec, variation allowed (±2 dB / ±3 % tempo) |
| ambience | loop-seam, variance floor (no dead air), band −30..−16 |
| music | seam, measured BPM (gaf-quality.py) vs spec, band, layers parity ±3 dB |
| voice | band, no music baked, subtitle mapping present |
| cinematics | wider range ok, bus routing verified |

## Audit findings (audio_audit.py) taxonomy

severity error|warning|info · categories asset|engine|mix ·
fix_kind fix (safe: resample/fade/trim/level → new file) | review (creative,
manual) | proposed (needs --apply). Repair ladder: safe-auto → approved →
manual → impossible; each fix re-measures before/after (report `recheck`).

## Release checklist (all must hold)

1. doctor READY · 2. every asset quality_status PASS (or WARNING accepted) ·
3. license_status set; commercial: approved or user-accepted ·
4. manifest `check` drift-free · 5. engine facts: no missing refs, voice
   budget within budget file · 6. playback states exercised (pause/scene
   change/restart) · 7. AUDIO_REVIEW_REQUIRED answered by a human ·
8. report lists every NOT_TESTED honestly (offline LUFS always).

## Test tiers

static (structure/frontmatter/router) → live-no-GPU (facts/ops on fixtures)
→ engine adapters (emit verified files) → GPU (gaf generations, backend's
gaf-test.sh 7/7) → manual listening. Each tier reports; none infers another.
