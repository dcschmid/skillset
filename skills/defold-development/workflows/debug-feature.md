# Workflow: Debug a Defold Feature

## Loop: reproduce → isolate → minimize → fix → regression-check

1. **Reproduce deterministically** — exact steps, one seed, one scene. If it
   only fails "sometimes", it's ordering/time/RNG: log seeds + message order.
2. **Read logs first** — engine + project logs
   (`references/debugging-testing.md`); most Defold breakage is message-id,
   URL, or resource-path typos visible in logs.
3. **Isolate the layer** — STATIC: lua byte-compile/lint the touched files;
   RUNTIME: attach debugger/DAP, break on suspect state transitions;
   engine-side (proxy/factory/render): check the docs page for the exact
   semantics you assumed — assumptions are the usual bug.
4. **Version-gate suspicion** — feature behaves per 1.9-era docs but project
   runs 1.14.x? Check `references/version-compatibility.md` change table
   (GLES2 opt-out, vector fonts, GLFW removal on mobile/HTML5).
5. **Minimize** — strip to smallest failing scene/script; fix there.
6. **Fix at the owner** — the module that owns the broken state, not a patch
   at the symptom site (no swallowing messages, no init-order sleeps).
7. **Regression** — assertion/test on the exact failing input; then the
   feature's existing checks. Report root cause + fix + level reached.

## Report format

Symptom · root cause (file:line) · fix · verified at level · residual risk.
