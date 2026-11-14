# UI & accessibility (4.7 baseline)

Style follows the game: pixel games → bitmap fonts + 9-slices; realistic 3D →
vector fonts + subtle themes. Structure is style-independent.

## Control stack

`Control`/`Container` layout via anchors + containers (zero hardcoded
positions for anything that rescales); `Theme` `.tres` shared across UI;
`CanvasLayer` HUD independent of camera. Localization: `tr()` + CSV/PO
translations; pseudolocalization pass (`--editor-pseudolocalization`) for
overflow before ship.

## Input routes (all three, always)

Keyboard: focus tree (`focus_neighbor_*`) + actions; controller: same actions,
`ui_*` nav signals; mouse: hover/focus parity. Focus visuals = visible focus
style, never color-only state.

## Accessibility gates (4.x AccessKit — verify per version)

Screen-reader tree on by default (`--accessibility auto`); set
accessible names/roles on custom controls; `--accessibility always` for CI
screenshot tests of a11y tree. Subtitles/legibility: user-scaled fonts via
theme defaults, contrast-checked palettes.

## Scaling matrix

`display/window/stretch/mode` + aspect (`expand`) tested at: base, 2×,
ultrawide 21:9, phone portrait/landscape. Pixel games: integer scale
(`pixel-art.md`). Text: no font size < 10 px at base res.

## Gates

RUNTIME with `--accessibility always` (tree present); VISUAL at each aspect;
controller-only navigation of every screen.
