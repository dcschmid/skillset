# Accessible UI patterns

These examples explain individual building blocks. Runnable fixtures live in
`../tooling/a11y-audit/fixtures/`, including clean, intentionally broken, and
dialog examples. Tests in `../tooling/a11y-audit/tests/` use these files.

## Native buttons

A real `button` supplies its role and keyboard interaction. Its text provides
the accessible name. Use `disabled` only when the action is unavailable.

```html
<button type="submit">Save</button>
```

A clickable `div` needs additional semantics and keyboard handling. Use the
native element for this action and provide visible focus styling.

## Inputs with help and errors

The label names the field. `aria-describedby` connects it to help and error
text. Set `aria-invalid="true"` only when the field is actually invalid.

```html
<label for="email">Email address</label>
<input id="email" name="email" type="email" autocomplete="email" required
       aria-describedby="email-help email-error" aria-invalid="true">
<p id="email-help">We use this address for order updates.</p>
<p id="email-error" role="alert">Enter a complete email address.</p>
```

After correction, clear the invalid state and remove the obsolete error
message. Include server-side validation failures in the checks.

## Dialogs and focus

```html
<button id="open" type="button">Edit record</button>
<dialog aria-labelledby="dialog-title">
  <h2 id="dialog-title">Edit record</h2>
  <button type="button">Close</button>
</dialog>
```

Markup alone does not open the dialog. Connect it to `showModal()` and a close
action in the project. Check initial focus, Tab and Shift+Tab, Escape, and focus
return to the trigger. Custom flows need explicit focus-return handling. A
working fixture is in `../tooling/a11y-audit/fixtures/dialog.html`.

## Announce status changes

Mount the status region before saving and update its content when the result
is available:

```html
<p role="status" aria-live="polite"></p>
```

For example, set its content to “Saved”. Reserve `role="alert"` for messages
that justify an interruption, rather than ordinary progress updates.

## Request a concrete check

```text
Use accessibility. Check our editing dialog while it is open. Test initial
focus, Tab, Shift+Tab, Escape, and focus return. Then check form validation
errors. Separate automated results, manual checks, and screen reader evidence.
```

Use this prompt in Claude Code, Codex, or oh-my-pi with the skill and required
tools installed. Automated checks alone do not establish WCAG conformance.
The [skill README](../README.md) covers setup and direct tool usage.
