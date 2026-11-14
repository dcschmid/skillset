# examples/

- `fixture-messy/` — seeded inconsistency corpus (dup buttons/cards, repeated
  hexes, scale scatter, `outline:none`, z-index sprawl) + a CLEAN token source.
  `ds.mjs audit` must FIND the problems; `ds.mjs tokens` must stay exit-0.
- `fixture-clean/` — the post-migration target: token-only styles, complete
  states, focus-visible, reduced-motion, no-flash theme script. Audit must
  stay quiet (0 P0/P1). Committed `tokens.css` carries the GENERATED banner.

The pair is asserted by `tests/run.mjs` (audit loud-on-dirty / quiet-on-clean,
token validation, deterministic build, report non-destructiveness). Don't
"fix" fixture-messy — tests assert the audit catches its flaws.
