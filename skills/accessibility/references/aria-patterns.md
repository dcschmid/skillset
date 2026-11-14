# ARIA patterns (APG-aligned, 2026-11-14)

Source: https://www.w3.org/TR/WCAG22/ + ARIA APG. Native element first;
ARIA only where platform gaps exist (APG is the recipe book).

## Naming precedence (understand before debugging names)

aria-labelledby > aria-label > <label> > native text > title > placeholder.
Name from content applies to button/link/tab. Visible label ⊆ accessible name
(2.5.3). `aria-describedby` for extra context (help text), never for the label.

## Pattern table (widget → required wiring)

| Widget | Base | Roles/states | Keyboard |
|---|---|---|---|
| Disclosure | button + region | `aria-expanded`, `aria-controls` | Enter/Space toggle |
| Tabs | native or div list | `tablist/tab/tabpanel`, `aria-selected`, roving `tabindex=0/-1` | ←→ Home End |
| Accordion | buttons | `aria-expanded` + heading wrapper | Enter/Space |
| Combobox | input + listbox | `role=combobox/listbox/option`, `aria-activedescendant`, `aria-controls/owns` | type + arrows + Esc |
| Modal dialog | `<dialog>` | labelled by title; `aria-modal` implicit on showModal | Tab cycles, Esc closes, focus returns |
| Menu | button + menu/menuitem | `aria-haspopup`, `aria-expanded` | arrows navigate, Enter activates, Esc closes |
| Toast/alert | `role=status`/`alert` | `aria-live` polite/assertive | none needed |
| Table | `<table><th scope>` | headers via ids only when complex | — |
| Slider | input[type=range] native | arrows change, Home/End | — |
| Tree | role=tree/treeitem/group | `aria-expanded` on branches | arrows |

Roving tabindex: exactly one widget stop, internal navigation by arrows;
Escape never leaves the page in the middle of the widget.

## State synchronization checklist

- every boolean state mirrors to DOM attr on change (`aria-selected` on tab switch)
- expanded/collapsed: one control, one state, both in name or state, never color
- disabled vs aria-disabled: native `disabled` removes from tab order — prefer `aria-disabled` + guard when focus must remain

## Forbidden moves (axe enforces some; rest is review)

- ARIA on presentational/generic where naming forbidden (`aria-prohibited-attr`)
- roles without required owned elements (list>listitem, tablist>tab)
- deprecated roles: `directory`, `definition`, `termslot`… replace (axe `aria-deprecated-role`)
- live region spam: one live region per concern, mounted on load, updated with content only

## Component API guidance

Expose `id` for `aria-labelledby`/`describedby` pass-through; accept
`label`, `describedBy` props; never hardcode ids (collision risk →
`useId()`/`crypto.randomUUID()` in SSR-safe frameworks).

Verify patterns against APG examples page before shipping novel widgets;
APG code is informative but canonical for interactions.
