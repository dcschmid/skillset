# Workflow: Implement One Gameplay Feature

Scope: one feature (movement, save, enemy type, HUD element…), not a
subsystem rewrite. Existing project truth wins (`existing-project.md` audit
already done).

## Steps

1. **Shape first** — find the closest system shape in
   `references/gameplay-systems.md`. Adopt its state-owner + message
   contract, or state why none fits. Do not invent a new framework.
2. **Name the owner** — one module writes the state; everyone else messages
   or reads. Write it down in the plan.
3. **Data before code** — tunables (speeds, damages, cooldowns) as
   properties/data tables, never inline literals in logic branches.
4. **Implement** — pure-Lua core where logic is testable, thin `.script`
   shell around it. Lifecycle callbacks only in `.script` files. Message ids
   hashed + centralized.
5. **Determinism check** — is this state replayed/rewound/ saved? Then fixed
   step, seeded RNG, no frame-delta.
6. **Test** — pure core: assertion harness/unit tests (see
   `references/debugging-testing.md`). Engine-side: AUTOTEST if harness
   exists, else RUNTIME log check.
7. **Report** — feature complete at which truth level; leftovers listed.

## Anti-rules

No speculative hooks "for the next feature"; no base classes; no global event
strings outside the project's message table.
