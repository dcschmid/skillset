# Migration (legacy UI → design system; incremental always)

Big-bang rewrites forbidden (brief §17). Every step leaves the app shippable.

## Order (10 steps, each independently revertable)

1. **Inventory:** `ds.mjs detect` + `ds.mjs audit` → component call sites,
   value scatter, token candidates. Output = migration backlog, ordered by
   (uses × pain).
2. **Convention freeze:** dir layout, styling mechanism, naming, export
   style — recorded from majority of existing code (audit report §conventions).
   New code obeys it; changing it is its own (rare) decision.
3. **Derive tokens from the design:** audit value index → primitives
   (exact repeated values) → semantics (meaning from usage context) →
   components (gaps only). Near-duplicate clusters = one design decision,
   recorded (winner + losers + rationale). Source: `tokens/`, NOT the app.
4. **Wire the pipeline:** tokens build → generated css/ts committed;
   app imports generated, never source. CI regeneration diff gate.
5. **Canonical components:** for each duplicated family (buttons, cards,
   forms, dialogs, nav): pick canonical (most-used & most-correct) →
   finish IT to the quality bar (states/types/a11y) → becomes the target API.
6. **Shim layer:** old component/import paths re-export canonical with an
   adapter for old props (marked `@deprecated — remove after <date>`). App
   keeps compiling untouched.
7. **Migrate call sites in waves** (page/module): mechanical via AST codemod
   when ≥10 sites, else per-file edit. After each wave: typecheck+tests+
   visual on touched routes. Old API diffs accumulate here = review surface.
8. **Visual regression per wave:** screenshot touched routes vs baseline
   (testing.md). Token-change fallout inspected — intentional deltas
   approved, accidental fixed before next wave.
9. **Delete legacy:** when shim refs = 0 (grep-verified twice: code+tests+
   stories), delete shim+old styles; run full checks. Dead styles/tokens die
   in the SAME wave that removes their last consumer — never "later".
10. **Close:** final `ds.mjs audit` delta + token stats + a11y spot-check →
    report (report workflow). Remaining P2/P3 = follow-up list, honest.

## Game UI (Godot/Defold): same order, engine artifacts
Theme resource / .theme GUI files replace generated CSS; call-site waves =
scenes/prefabs; screenshot diff via engine headless capture.

## Risks
- **Two systems mid-flight** is the normal state: shims + boundary rules
  (no new code on legacy API after step 5) keep it finite. Date every shim.
- **Silent style drift** on shared components: mitigate with baseline
  screenshots BEFORE wave 1 (baseline = reviewed current truth, brief §15).
- **Token bikeshed** blocking waves: primitives ship frozen-ish; naming
  debate happens on semantics only, in the report, not in PRs.
- Rollback = per-wave revert; generated files regenerate, never hand-patch.
