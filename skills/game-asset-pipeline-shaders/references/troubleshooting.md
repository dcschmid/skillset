# Troubleshooting

| Symptom | First checks | Fix class |
|---|---|---|
| texture black after import | color space slot (data maps linear); alpha mode; engine import preset | config, reversible |
| atlas bleeding | filter vs gutter; premultiply on resize | padding/filter config |
| pixel-art blurry | mips on / linear filter / lossy resample applied | style config, never re-lossy the original |
| verts blow up on export | UV seams + hard edges + material splits split verts | expected; budget in post-export count |
| model wrong scale/up-axis | Blender +Z/+Y vs engine; export apply-transform flag | export preset |
| animation lost in GLB | actions not assigned / joints not in skin / export_selection trimmed armature | export scope |
| procedural material = white blob in engine | Blender nodes ≠ glTF; bake or rebuild engine-side | bake + new deliverable |
| Draco/meshopt asset fails import | decoder absent in engine/platform | re-export uncompressed |
| shader compiles external, fails engine | dialect/version mismatch — engine-side compile is truth | adapter dialect fix |
| VRAM over budget, files small | block-format VRAM ≠ file size; mip chain; dup textures | dedupe + codec per profile |
| fix tool broke a look | diff vs `.orig`/VCS; restore; downgrade fix to suggestion | revert, re-approve |
| report shows green but test never ran | check `validation` per finding; NOT_RUN lines | honest re-report |
| empty audit on valid project | `asset-pipeline.yaml` exclude globs swallowing assets | config globs |

Escalation: unresolved → minimal repro (one asset, headless engine import),
cite exact command+output; unknowns stay UNVERIFIED in the report.
