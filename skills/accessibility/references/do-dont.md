# Do / Don't — current practice (verified vs W3C docs 2026-11-14)

Format: DO · DON'T · WHY · SC · CODE · TEST. Newest-AVG patterns first.

## 1. Native first, ARIA second

- **DO**: `<button>`, `<a>`, `<input>` + `<label for>`, `<dialog>`, heading levels, `<table>` semantics.
- **DON'T**: `<div role="button" tabindex="0">` where a `<button>` works; `role` duplicating implicit role.
- **WHY**: native elements ship focus, keyboard, SR announcements; ARIA only changes the accessibility tree, not behavior.
- **SC**: 4.1.2, 1.3.1, 2.1.1.
- **CODE**: ✅ `<button aria-expanded={open}>Menu</button>` ❌ `<div class="btn" onClick={…}>Menu</div>`
- **TEST**: axe rules `aria-*`, `nested-interactive`; SR announcement spot-check.

## 2. Labels

- **DO**: `<label for>` or wrapping label; `aria-labelledby` when visible text lives elsewhere.
- **DON'T**: placeholder as label; `aria-label` overriding a visible label inconsistently (2.5.3).
- **SC**: 3.3.2, 4.1.2, 2.5.3.
- **CODE**: ✅ `<input id="q"><label for="q">Search</label>` ❌ `<input placeholder="Search">`
- **TEST**: axe `label`; SR: "does every field announce its purpose before input?"

## 3. aria-hidden & focus

- **DO**: `inert` (or `aria-hidden` + `tabindex=-1` fallback) only on closed overlays' content; keep focusables out.
- **DON'T**: `aria-hidden="true"` on regions containing tabbables; hiding still-focusable content.
- **SC**: 2.4.3, 4.1.2.
- **TEST**: `a11y keyboard` — hidden-but-focusable stops flagged; `aria-hidden-focus` axe rule.

## 4. Focus indicators

- **DO**: `:focus-visible { outline: 3px solid Highlight }` — never remove without replacement; honor `outline` in forced-colors.
- **DON'T**: `outline: none` with a custom ring <2 px or color-only.
- **SC**: 2.4.7, 2.4.11 (AA), 1.4.11.
- **TEST**: keyboard walk + screenshots at 400 % zoom; manual: "can you see every stop?"

## 5. Status messages

- **DO**: `role="status"` (polite) for saves/filters; `role="alert"` only for errors needing interruption.
- **DON'T**: live regions mounted from page start that mutate on every keystroke; announcing whole page after route change.
- **SC**: 4.1.3.
- **TEST**: SR test with real speech capture (screenreaders.md).

## 6. Dialogs

- **DO**: `<dialog>` + `showModal()` (native focus trap + Escape); focus first field; return focus to opener.
- **DON'T**: custom overlay without trap; dialog with focusables still visible under backdrop.
- **SC**: 2.1.2, 2.4.3, 4.1.2.
- **TEST**: `a11y audit --config` scenario with `expect` after open (tooling/a11y-audit/fixtures/dialog.html).

## 7. Forms & auth (3.3.7, 3.3.8)

- **DO**: autocomplete attrs, paste allowed, `required` + `aria-describedby` help text, errors `aria-describedby`-linked, confirm step for destructive/legal input.
- **DON'T**: forced password rules w/o hint; re-asking data already given in flow; image-CAPTCHA without audio alt.
- **SC**: 3.3.2, 3.3.3, 3.3.7, 3.3.8, 1.3.5.

## 8. Interaction surface (2.5.x)

- **DO**: pointerup activation; drag alternatives; ≥24 px targets (44 on touch), 8 px gaps when tight.
- **DON'T**: `mousedown` handlers, double-click-only flows, hover-only menus w/o click/tap twin.
- **TEST**: `target-size` rule automated; gesture twins manual.

## 9. Motion & adaptation

- **DO**: `@media (prefers-reduced-motion: reduce)` → disable auto motion; honor `prefers-contrast`, forced-colors for tokens.
- **DON'T**: infinite autoplay carousels without pause; `background: white` hardcoded killing dark mode contrast.
- **SC**: 2.3.3 (AAA), 1.4.12, 1.4.4.

## 10. Overlays & "a11y plugins"

- **DO**: fix source code. **DON'T**: third-party accessibility overlays as a substitute; they patch symptoms, break SR flow, and audit reports must not credit them.
- **WHY**: injected DOM confuses names/relationships; cannot supply missing semantics reliably.

## 11. Reports honesty

- **DO**: statuses PASS / FAIL / NEEDS MANUAL REVIEW / N/A / NOT TESTED; missing ≠ pass.
- **DON'T**: claim "WCAG compliant" from axe-green alone (~30–50 % of SC are undecidable from DOM).
- **TEST**: audit-methodology.md manual slice.

## Deprecated / disputed recommendations (keep list growing)

- `tabindex="5"`+ positive values — breaks order everywhere.
- `role="application"` on normal widgets — silences SR browse mode.
- `aria-label` on `<p>`/generic containers to "fix" SR reading — fix structure instead.
- h1→h3 jumps "for SEO" — SEO myth; hurts SR navigation.
- `<div onClick>` + React synthetic keydown mimics — use `<button>`.
- auto-advancing focus ("skip ahead" patterns) — breaks SR users mid-page (WCAG 3.2.x).
- Orca test claims without Orca running — label DOM checks as DOM checks.
