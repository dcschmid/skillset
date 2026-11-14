# Export & release (4.7 baseline)

## Presets & CLI (verified command surface)

`export_presets.cfg` committed; named presets per platform. CI export:

```
godot --headless --path . --export-release "Windows Desktop" builds/game.exe
godot --headless --path . --export-pack  "Linux/X11"        builds/game.pck
godot --export-debug / --export-pack (PCK|ZIP by extension) / --export-patch
```

Export templates installed per engine version (`Editor > Manage Export
Templates`); CI caches them keyed on version hash — never `latest`.

## Platform matrix (verify per pinned version before promising)

| Target | Notes |
|---|---|
| Linux/Windows/macOS | desktop exporters; macOS = .app bundle + notarization external |
| Web (HTML5) | renderer constraints (verify WebGPU/GL state per minor); host needs COOP/COEP headers for threads; serve over HTTPS-ish host |
| Android/iOS | SDK toolchains, `--install-android-build-template`; device perf floors dominate |
| Consoles | official exporter channels exist for the 4.x era — verify per platform page |

C#: mono export templates only; verify per-version platform support before
committing a language to a platform slate.

## Release checklist

1. Version gate: engine + addons pinned in README (`godot-versions.md` routine).
2. Ladder green: STATIC → IMPORTED → RUNTIME (headless) → BUILT per platform →
   VISUAL spot on installed build.
3. Reproducible: two `--export-pack` runs → same content hash (deterministic
   packing; strip local paths via export filters, verify filters exclude
   `tests/`, editor scratch).
4. Save-compat: save from previous version loads (versioned payloads).
5. Assets: license credits shipped; font subsets; compression per platform.
6. Store lanes (Steam/itch.io): depot/zip layout, launch args, controller
   prompts — platform docs at upload time, not folklore.

## Non-destructive

Builds under `builds/` (gitignored); collisions dated-suffix.
