# Licensing (commercial release gate)

Open-source runtime ≠ free content. Check layers separately; the manifest
carries `license_status: approved|review_required|restricted|unknown` per
asset (backend docs/LICENSES.md is the source of truth, re-verify upstream
before shipping — claims there are dated).

| Component | runtime | weights | commercial |
|---|---|---|---|
| acestep.cpp / ACE-Step 1.5 | MIT | MIT ("commercial use explicitly fine") | approved |
| sa3.cpp / Stable Audio 3 small-sfx | MIT | Stability Community | ✅ while <$1M/yr revenue; above → enterprise licence + registration + "Powered by Stability AI" → **review_required** for commercial unless tier confirmed |
| audiogen.cpp / Dasheng (legacy) | NO LICENSE FILE | Apache-2.0 | weights clean, runtime unlicensed → restricted: internal/experiments only, never in commercial builds |
| ffmpeg | LGPL/GPL dyn | — | ok dynamic |
| CUDA | NVIDIA EULA | — | proprietary-ok |

## Rules

- `audio_manifest.py` seeds status from the sidecar generator note:
  ACE-Step→approved, SA3→review_required, dasheng→restricted, imported→
  unknown until reviewed. `unknown` never passes a commercial release check
  silently — it blocks or is explicitly accepted by the user.
- Voice samples / reference audio: rights + consent are the importer's
  responsibility; status stays `unknown`/`review_required` until documented.
- Release gate: `audio_manifest.py check` + every asset license_status ∈
  {approved} (or user-accepted review_required with revenue tier written
  down). Restricted/unknown → list in report as shipping risk.
