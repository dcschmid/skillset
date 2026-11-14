# Design Tokens — DTCG v2025.10 + 3-tier architecture

Spec status (probe 2026-11-14): **v2025.10 = first stable** (CG-Final,
2025-10-28, `designtokens.org/TR/2025.10/`). `$themes`/`$media` conditional
tokens = **draft** → emit only with `--experimental` intent, never as
required output. `$extend` = new in 2025.10, treat as recent (tool support
thin). Pre-2025.10 "DTCG-ish" files (bare `value`/`type`) are common
in the wild → ds.mjs accepts both, prefers `$`-keys.

## Source layout (edit these; never the output)

```
tokens/
  primitives.tokens.json   # raw: palettes, scale numbers, fonts — no meaning
  semantic.tokens.json     # meaning: background-primary… aliases primitives
  components.tokens.json   # optional: per-component, only real gaps
  themes/<name>.tokens.json# optional brand themes (alias semantic layer)
build/…                    # GENERATED: css/tokens.css, tokens.ts — read-only
```

## DTCG shape

```json
{ "color": {
    "blue-500": { "$type": "color", "$value": "#457b9d",
                  "$description": "…", "$extensions": { "com.example.deprecated": true } } },
  "size": { "md": { "$type": "dimension", "$value": "1rem" } } }
```
- `$type` propagates down groups; types: color, dimension, fontFamily,
  fontWeight, duration, number, cubicBezier, gradient, shadow, image, link,
  `com.*` custom. Alias = `"$value": "{group.name}"` — pure string, whole value.
- No alias-with-modifier (`{x} + 2px` invalid). No array-alias mixing.
- Deprecation: no spec field → `$extensions.deprecated` (ds.mjs reports).

## Three tiers + naming

| Tier | Example | Consumers |
|---|---|---|
| Primitive | `color.blue-500`, `size.4` | only semantic tier |
| Semantic | `background-primary`, `text-muted`, `action-primary`, `focus-indicator`, `status-error` | components (STOP HERE) |
| Component | `button-primary-hover`, `modal-overlay` | one component, when semantic can't express |

Rules (binding):
1. Components reference semantic tokens; touching a primitive from a
   component = finding (unless no semantic exists → create semantic first).
2. Alias downward: semantic→primitive, component→semantic. Never upward, never sideways chains >2 deep.
3. **Anti-explosion:** new token needs ≥3 usages OR a genuine semantic gap.
   One-off variation → component prop or local style, not a token. Cycles/
   missing aliases are P0 (ds.mjs exits 1).
4. Names follow the PROJECT (camelCase project keeps camelCase). Kebab shown
   here is the neutral default when the project has none.
5. Themes = override map of **semantic** layer (see theming.md); primitives
   are theme-independent.

## Validate → build → consume

```bash
node scripts/ds.mjs tokens tokens/semantic.tokens.json --themes light,dark
```
Checks: DTCG shape, unknown $type, missing/cyclic aliases (P0), type↔value
mismatch, theme parity (P1), duplicate values + name collisions (P3),
deprecated count. Exit 1 on P0 → CI gate.

Build output (reproducible, committed source → deterministic artifact):
- CSS custom props `:root` + `[data-theme=dark]` blocks, kebab-cased names.
- TS module `as const` (typed, tree-shakeable) when TS project.
Use `assets/ds-tokens-build.mjs` (zero-dep) when the project has no Style
Dictionary. Style Dictionary v5 (ESM config) only when project already
depends on it — its `outputReferences` for alias preservation stays
experimental; don't depend on it.
CI: regeneration check = build to temp, diff vs committed generated files.

## Figma / Tokens Studio boundary

Figma Variables & Tokens Studio speak DTCG for import/export. Round-trip:
DTCG JSON is the interchange, local `tokens/*.json` stays the source of
truth; plugin sync is one-way per change (Figma→repo PR or repo→Figma push),
never bidirectional-live. $extensions carries `com.figma.*` hints untouched.

## Migration from scattered values

1. `ds.mjs audit` → hardcoded-value index (hex/rem/font-size occurrence map).
2. Values with ≥2 uses → candidate primitive; cluster near-duplicates
   (#3f5f7f vs #457b9d = ONE token, pick winner, note the decision).
3. Name from meaning-in-use, ship source + generated, then fix call sites
   (references/migration.md order).
