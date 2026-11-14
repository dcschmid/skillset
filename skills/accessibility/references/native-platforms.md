# Native platforms — desktop apps, mobile apps, games

Web WCAG ≠ full proof for native. Map to the right baseline: WCAG2ICT (WCAG
applied to non-web ICT via ICT-specific interpretation) + platform
accessibility APIs. EN 301 549 clauses 5.1–13 govern most native ICT.

## Desktop apps

### GTK (Linux native)
- ATK/GAIL → AT-SPI2 tree; verify with Accerciser while Orca attached.
- Check: widget names from `gtk_widget_set_tooltip_text`/label relations,
  mnemonics, focus chain matches tab order, GtkDialog trap semantics.

### Qt (Linux/Windows)
- `QAccessible` interface; set `QAccessible::Name/Description/Role` via
  `setAccessibleName`, buddy labels, tab order (`setTabOrder`).
- Test: NVDA/Orca read fields; `QT_ACCESSIBILITY=1` env on Linux.

### Windows native (WinUI/WPF/Win32)
- UIA tree: AutomationProperties.Name/LabeledBy/HelpText; `IsTabStop`,
  `AutomationPeer` for custom controls. NVDA + Narrator verify.

### macOS (AppKit/SwiftUI)
- NSAccessibility protocol / `.accessibilityLabel()` modifiers; focus ring
  follows keyboard; VoiceOver + macOS Accessibility Inspector.

Common requirements regardless (EN 301 549 §5.1–5.6 analogues):
text alternatives, captions for media, focus visible, keyboard operable,
contrast of UI (3:1 non-text), magnifier-friendly DPI scaling.

## Mobile apps

- Android: `contentDescription`, `labelFor`, `importantForAccessibility`;
  TalkBack gesture order; `accessibilityPaneTitle` for dialogs.
- iOS: UIAccessibility labels/traits, `accessibilityElement(children:)`,
  rotor entries; VoiceOver verbosity.
- Verify with device SRs manually (mobile automation for SRs is unreliable —
  document "manual device testing" as method, never fabricate).

## Games (Defold/Godot/Unity engines)

Game content is not document-like; apply via WCAG2ICT principles +
platform docs (Defold: label/element `aria`-style metadata limited; Godot:
Control nodes have accessibility names; Unity: UI toolkit a11y):
- remappable keybindings + full input w/o mouse
- captions/subtitles for spoken content; text scaling ≥ 200 % without clipping
- colorblind-safe palettes (never color-only for health/teams/damage)
- readable HUD contrast, HUD scaling, reduced motion options (camera shake)
- skip/pace control for time pressure where feasible (2.2.x analogues)
- difficulty/repeatable checkpoints to avoid memory under time limits (3.3.x)
Deliver: an a11y-options screen (captions on/off, size, contrast themes) and
test with the platform SR (TalkBack/Orca) over the engine's HUD where the
engine exposes a11y tree; otherwise manual device checks + screenshots as
evidence. EN 301 549 chapter 11 (non-text content) + 5.x apply to game *UI*
(menus/overlays) more strictly than gameplay.

## Reporting

For native: state baseline ("WCAG2ICT via EN 301 549 5.x + platform API"),
method (platform AT = real SR; engine a11y tree dump = DOM-analogue), and
what web WCAG tooling CANNOT certify. Never emit a "WCAG 2.2 AA conformant"
line for native from web tools.
