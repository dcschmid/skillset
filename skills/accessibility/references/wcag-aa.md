# WCAG 2.2 A/AA — working checklist (all 50 SC, dev-time view)

Levels A+AA are the floor. Each line: SC · one-line test a developer can run.
Full text: https://www.w3.org/TR/WCAG22/; rationale: Understanding docs.

## Perceivable

- **1.1.1 Non-text Content (A)**: every `<img>` has `alt` (informative) or `alt=""` (decorative). `a11y audit` rule `image-alt`.
- **1.2.1 Audio-only/Video-only Prerecorded (A)**: transcript for audio; captions path for video. Manual-leaning.
- **1.2.2 Captions Prerecorded (A)**: captions on all prerecorded video with audio.
- **1.2.3 Audio Description or Media Alternative (A)**: alt for video content/AD.
- **1.2.4 Captions Live (AA)**: live captions mechanism.
- **1.2.5 Audio Description Prerecorded (AA)**: AD track for video.
- **1.3.1 Info and Relationships (A)**: headings h1→h2→…, real lists/tables, `<label>`s, fieldsets. Auto: 8 axe rules.
- **1.3.2 Meaningful Sequence (A)**: DOM order = reading order; no layout grid-row tricks that scramble SR order.
- **1.3.3 Sensory Characteristics (A)**: instructions never only "the red one on the left".
- **1.4.1 Use of Color (A)**: color never sole signal (links get underline/weight too; charts add labels/patterns).
- **1.4.2 Audio Control (A)**: >3 s auto audio pausable.
- **1.4.3 Contrast Minimum (AA)**: 4.5:1 body, 3:1 large (24px/18.66px bold). Auto: `color-contrast`.
- **1.4.4 Resize Text (AA)**: 200 % zoom without loss/content loss. Auto partial: `meta-viewport`.
- **1.4.5 Images of Text (AA)**: real text, styled.
- **1.4.10 Reflow (AA)**: 320 px CSS px wide, no 2-D scroll (≈ mobile 375 viewport check).
- **1.4.11 Non-text Contrast (AA)**: 3:1 for borders, focus rings, icons, chart strokes against adjacent colors.
- **1.4.12 Text Spacing (AA)**: user line/space overrides don't clip.
- **1.4.13 Content on Hover or Focus (AA)**: dismissible (Esc), hoverable, persistent tooltips.

## Operable

- **2.1.1 Keyboard (A)** / **2.1.2 No Keyboard Trap (A)**: Tab loop reaches everything, leaves everything.
- **2.2.1 Timing Adjustable (A)**: session timeouts extendable/off.
- **2.2.2 Pause Stop Hide (A)**: moving/auto-updating >5 s pausable.
- **2.3.1 Three Flashes (A)**: ≤3 flashes/s.
- **2.4.1 Bypass Blocks (A)**: skip link or landmarks.
- **2.4.2 Page Titled (A)**: unique `<title>`.
- **2.4.3 Focus Order (A)**: sequential; widgets restore focus on close. Manual: order logic.
- **2.4.4 Link Purpose (A)**: link text ≠ "click here" alone; context may complete it.
- **2.5.1 Pointer Gesture (A)**: multipoint/sequence gestures have single-pointer alternative.
- **2.5.2 Pointer Cancellation (A)**: click actions fire on up, not down.
- **2.5.3 Label in Name (A)**: visible label ⊂ accessible name.
- **2.5.4 Motion Actuation (A)**: gesture input has button alternative.
- **2.5.7 Dragging Movements (AA, new 2.2)**: drag has single-pointer/keyboard alternative.
- **2.5.8 Target Size Minimum (AA, new 2.2)**: ≥24×24 px targets or spacing rule. Auto: `target-size`.

## Understandable

- **3.1.1 Language of Page (A)**: `<html lang>`. **3.1.2 Language of Parts (AA)**: `lang` on passages.
- **3.2.1/3.2.2 On Focus/On Input (A)**: focus/change never jumps context unexpectedly.
- **3.2.4 Consistent Navigation / 3.2.6 Consistent Help (AA, new 2.2)**: contact/help placed consistently.
- **3.3.1 Error Identification (A)**: errors describe the problem in text, linked to field.
- **3.3.2 Labels or Instructions (A)**: labels before input; placeholder ≠ label.
- **3.3.3 Error Suggestion (AA)**: recoverable errors get fix suggestions.
- **3.3.4 Error Prevention Legal/Financial (AA)**: review/confirm step.

## Robust

- **4.1.1 Parsing (A)**: unique ids, complete tags (axe: duplicate-id*).
- **4.1.2 Name Role Value (A)**: controls expose name/role/state via native semantics first.
- **4.1.3 Status Messages (AA)**: `role=status`/`aria-live` for async feedback.

## WCAG 2.2 delta (all new in 2.2)

| SC | Level | Dev obligation |
|---|---|---|
| 2.4.11 Focus Not Obscured Minimum | AA | focus indicator ≥ half-visible vs sticky/overlays |
| 2.4.12 Focus Not Obscured (Enhanced) | AAA | fully visible |
| 2.4.13 Focus Appearance | AAA | ≥2 px perimeter, 3:1 against adjacent |
| 2.5.7 Dragging Movements | AA | alternative for drag |
| 2.5.8 Target Size Minimum | AA | 24 px or spacing |
| 3.2.6 Consistent Help | AA | help entry same place per page |
| 3.3.7 Redundant Entry | AA | never re-ask in-flow data |
| 3.3.8 Accessible Authentication | AA | no cognitive test w/o alt; paste + autofill allowed |

Test each delta in your app, not just via axe (target-size is automated;
the rest mostly need scenario tests — keyboard-testing.md).
