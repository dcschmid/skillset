# Accessibility — WCAG 2.2 AA gate

Semantic HTML first, ARIA only to fill real gaps. Every interactive component
ships: keyboard path, visible focus, announced state, reduced-motion fallback.

## Component checklist (delivery-blocking)

- **Keyboard:** all interactions reachable and operable (Tab order follows
  visual; dialogs trap focus + Esc closes; custom widgets implement
  roving-tabindex or use a headless lib that does).
- **Focus visibility:** `:focus-visible` styles in the token set; never
  `outline:none` without a replacement.
- **Names & roles:** native elements carry their own; icon-only controls get
  `aria-label`; custom controls get role+state only when no native element
  exists (button/div-with-onClick → use `<button>`).
- **Forms:** `<label for>` or wrapped; errors linked via `aria-describedby`,
  announced on submit attempt; required marked + communicated in text.
- **Live content:** async results announced (`aria-live="polite"` region for
  toasts/filters); loading states not screen-reader-spam (debounce).
- **Contrast:** text ≥ 4.5:1 (3:1 large); UI states 3:1; token pairs tested
  light+dark.
- **Motion:** all animation inside `prefers-reduced-motion` guards;
  ViewTransition usage degrades (styling.md, react-modern-apis.md).
- **Touch:** targets ≥ 24×24 CSS px (44 preferred on mobile-first), spacing
  between targets.

## Framework specifics

- Next App Router: route-change announcements for SPAs — announce on
  pathname change (polite live region or focus-move to `h1`); `<Link>` stays
  real anchor.
- Suspense/streaming: fallbacks carry dimensions (CLS) and don't steal focus;
  skeleton markup `aria-hidden` where decorative.
- Server Components render standard DOM → normal a11y applies; no client-only
  polyglot gaps: interactive islands still keyboard-first.
- Headless libs (Radix et al.) ship a11y-correct; don't re-skin into
  brokenness — keep their roles/labels.

## Verification

1. Static: axe-core pass in tests (testing.md) on key routes/components.
2. Manual keyboard walk: load → primary flows → error states; focus order sane.
3. Screen-reader spot check (VoiceOver/NVDA): page title, landmarks, form
   errors, dynamic updates.
4. Contrast: tokens audited once at source; components inherit.

Claims: "tested via axe + keyboard walk of <flows>" or list the gap — never
"accessible by construction".
