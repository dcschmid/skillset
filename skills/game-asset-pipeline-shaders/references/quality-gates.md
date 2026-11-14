# Quality gates + CI

Gate = named pass/fail over findings. Asset ships only with all required
gates at their required truth level; a gate whose tests did not run reports
`NOT_RUN`, never green.

| Gate | Pass = | Min level |
|---|---|---|
| G1 asset-validity | parse+refs resolve, 0 Critical | STATIC |
| G2 material-integrity | no Critical/High defects (style notes exempt) | STATIC |
| G3 shader-compat | engine compile ok, variant count ≤ budget | HEADLESS |
| G4 render-consistency | compare within project thresholds | RENDER |
| G5 budgets | measured/estimated ≤ profile | STATIC(est) ok, labeled |
| G6 engine-import | headless import 0 errors | HEADLESS |
| G7 platform-compat | formats ⊆ adapter table | STATIC |

## Report contract (every finding)

`file · category · severity(Critical/High/Medium/Low/Informational) ·
description · cause(when known) · fix(suggestion or applied) · impact ·
validation(STATIC|HEADLESS|RENDER|MEASURED|NOT_RUN:<why>)`

Outputs: JSON (CI/`jq`) + Markdown (devs) + optional HTML.
`asset_report.py`/scripts emit both JSON+MD.

## CI (headless, reproducible)

`pipeline_runner.py audit --json` on asset paths as a check step; fail on
Critical (and High if project sets it); `compare` on changed assets when a
renderer exists in CI. No installs in CI; missing optional tools degrade to
STATIC gate + warning, gate stays honest about its level.
