# Testing & CI (4.7 baseline)

## Ladder (mirrors SKILL.md truth levels)

| Gate | Command | CI-fails-on |
|---|---|---|
| Script parse | `godot --headless --check-only --script f.gd` (per `.gd`) | parse errors |
| Project import | `godot --headless --import .` | broken deps/missing assets |
| Boot | `godot --headless --path . --quit-after N` | runtime script errors |
| Scene smoke | boot each scene: `godot --headless res://scenes/x.tscn --quit-after N` (verify per-scene CLI per version) | per-scene boot errors |
| Unit | gdUnit4 (`gdunit4` CLI) or GUT (`gut` CLI) headless | assertion fails |
| Movie | `--write-movie out.avi --fixed-fps 60 --quit-after N` | nondeterministic frames |

`--headless` = display-driver headless + dummy audio: CI-safe everywhere a
binary runs. Renderer under headless still exercises shaders for checks.

## Framework choice (opt-in dependency)

gdUnit4 and GUT both ship CLI/headless runners — pick ONE, pin version in
README, run via engine binary in CI. stdlib-only fallback: throwaway
`SceneTree` scripts run with `--script` + `get_tree().quit()` asserting
(`scripts/headless_check.sh` shows the shape). No framework for prototypes —
import+boot gates are the baseline.

## Style-aware asserts

Pixel: assert `default_texture_filter` + stretch settings in
`project.godot` (audit script). Voxel: chunk save/load byte-equality test.
3D: material/anim-list presence. UI: `--accessibility always` tree check.
Multiplayer: two headless instances join/leave.

## CI skeleton (GitHub Actions sketch)

```yaml
- run: godot --headless --import .
- run: find . -name '*.gd' -exec godot --headless --check-only --script {} \;
- run: godot --headless --path . --quit-after 120
```

Engine pinned by URL+version in workflow (never `latest`); export templates
cached; artifacts: logs + movie.

## Reporting

Every run reports LEVEL + command + observed tail. No binary → report
UNVERIFIED with commands; invented PASS forbidden.
