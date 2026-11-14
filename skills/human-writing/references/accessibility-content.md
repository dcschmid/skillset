# Accessibility content (WCAG 2.2 AA binding, AAA advisory)

Language layer of a11y; coordinates with the standalone accessibility skill
(which takes precedence on structural a11y questions). Text-level rules:

- Plain, understandable wording at the target audience's level; abbreviations
  expanded at first use where the reader needs it.
- Link text describes its destination (3.2.4 consistent help, 2.4.4 purpose).
- Buttons: verb + object ("Save profile"), error messages: what + next step,
  no blame, consistent terminology (3.3.2 labels/instructions).
- Alt text names what the image contributes; decorative stays empty alt.
- Headings describe their section; heading level order intact.
- Form labels match visible text; error text survives screen readers.
- Language marking (html lang) present and correct; mixed-language runs keep
  their own lang where meaningful (3.1.x).
- Consistent naming across pages (3.2.3/3.2.4).
- `lang` attribute on audit: the auditor reports missing/mismatched `html lang`.

Do not edit ARIA, roles, focus handling, or landmark structure as part of a
prose pass — flag for the a11y lane. Simplified phrasing must never remove
meaning (AAA advisory: plain language without loss of precision).
