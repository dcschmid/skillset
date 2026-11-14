# Screenreader testing — real vs simulated, platform truth

Test types (NEVER interchange the labels in reports):

| Kind | Evidence | Counts as |
|---|---|---|
| Real SR test | speech/braille captured from running Orca/NVDA/VoiceOver | SR test (nameable) |
| Virtual SR (Guidepup virtual-screen-reader) | simulated announcements from DOM | DOM/AT-tree test, NOT SR |
| axe-core rules | computed properties | automated rule check |
| AT-SPI/AX tree dump | platform tree snapshot | tree inspection |

## Linux (Fedora/KDE/Wayland) — host truth (probed 2026-11-14)

- Orca 50.3, AT-SPI2 2.60.7, session bus at /run/user/1000/bus; AT-SPI bus
  at /run/user/1000/at-spi/bus_0. Firefox 159 system + Playwright builds.
- Guidepup (@guidepup/guidepup 0.40.0) drives Orca via its own bundled
  Orca build (assets under ~/.cache/guidepup/orca, project-scope install via
  `npx @guidepup/setup install` — no system package changes).
- Constraints found (Fedora KDE Wayland):
  1. Orca and speech-dispatcher are single-instance per session. A user-run
     Orca blocks Guidepup's managed Orca (`--replace` semantics conflict);
     kill user Orca before SR automation.
  2. speech-dispatcher must not be running unmanaged, else Guidepup's private
     socket never appears → "Orca cannot be started".
  3. Firefox must have accessibility enabled; Playwright launches expose AT
     tree only when an AT is attached (Guidepup handles via AT-SPI).
  4. Wayland: Guidepup uses AT-SPI + D-Bus, NOT XTest, so Wayland itself is
     not the blocker — but no X11-only fallbacks (xdotool-style) exist.
  5. KDE kaccess may auto-start Orca-like behavior; check `ps` before runs.
- Run: `node tooling/a11y-audit/tests/screenreader-orca.ts` prints
  SR_PASS / SR_INCOMPLETE / SR_ENV_FAIL and writes sr-speech.json (evidence).

## Windows / macOS (for reports on those hosts)

- NVDA + Firefox/Chromium: Guidepup NVDA support; needs NVDA running +
  `npx @guidepup/setup install`. VoiceOver + Safari on macOS: Guidepup
  VoiceOver class; enable "VO commands from keyboard" off caveats apply.
- Never claim SR_PASS on hosts where the SR did not run.

## Mobile (manual workflows — no automation claims)

- Android + TalkBack: Settings → Accessibility → TalkBack ON. Test: swipe
  left/right per element; confirm name→role→value order; forms announce
  label before edit; dialog opens announce title; error = assertive announce.
  Log: record screen + narrate findings (screen recording = evidence).
- iOS + VoiceOver: same pattern; rotor for headings; confirm 3.3.x announcements.

## What a real SR test must capture (evidence contract)

1. SR version + host OS. 2. navigation command issued. 3. spoken phrase log.
4. expected vs observed diff. Our harness: out/sr-speech.json + sr-verdict.txt.

## Scenarios worth SR automation (in priority order)

1. page load announcements (title, h1, landmarks)
2. form labels + required + error flow (3.3.1/3.3.2/4.1.2)
3. dialog open/type/submit/close + focus return (2.4.3)
4. live region updates (4.1.3)
5. table header association (1.3.1)
6. heading navigation order (2.4.6)

Manual fallback stays documented for CI/containers without AT-SPI: use the
checklists in keyboard-testing.md + audit-methodology.md manual queue.
