# Unicode & RTL — enforcement points inside this skill

## Unicode (scripts enforce; verify with graphemes, never codepoints)
- all catalogs read/written UTF-8; BOM stripped on parse, not silently kept
- `graphemeCount` = `Intl.Segmenter('und',{granularity:'grapheme'})` — layout
  math and expansion percentages are grapheme-based
- mojibake detection (double-encoded UTF-8: Ã©, â€) = HIGH confirmed
- control chars/BOM inside strings flagged (LOW unless mojibake)
- combining accents/emoji sequences survive pseudo runs (accent map is
  composed-character based; placeholder spans masked before mapping)
- number/date/currency: ICU/Intl at runtime in frameworks; catalogs store
  placeholders, never locale-shaped literals (`{amount}` not `1.234,56`)
- sort/search: engine APIs (Collator, Godot `compare_locales`, SQL ICU);
  skill does not re-implement

## RTL (ar/he/fa/ur/…)
- `isRtl()` drives: `dir` attrs, pivot swaps, isolate-wrapped pseudo output
- web: `<html lang>` + `dir`, CSS logical properties (inset-inline,
  margin-inline), `dir="auto"` for user-generated text, `<bdi>` for mixed
  spans; no blanket mirror — logos, media controls, coordinates, gameplay
  arrows are per-asset decisions
- bidi: U+202B/202C isolates around RTL pseudo strings; mixed latin+digits
  inside RTL strings → INFO `rtl-isolation` at render site
- Defold: pivot West↔East swap + full-font-layout appmanifest (docs-verified);
  Godot: right_to_left_mode; engine shaping stack documented per adapter
- a real RTL test needs a rendered surface — without one, report NOT TESTED
