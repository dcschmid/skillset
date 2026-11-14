# Examples

Runnable in-repo: `tooling/a11y-audit/fixtures/` (clean/broken/dialog) are the
live examples validated by `tests/run.mjs`.

## Accessible button (framework-neutral truth)

```html
<!-- ✅ name from content, keyboard, focus, disabled state: all native -->
<button type="submit" disabled>Save</button>
```
```tsx
// ✅ React/Next/Astro island: same element, props typed
export function Button({ label, ...rest }: React.ComponentProps<'button'>) {
  return <button {...rest} className="btn focus-visible:outline-3">{label}</button>;
}
```
```astro
<!-- ❌ Astro: div-as-button: no SR role, no keyboard — delete on sight -->
<div class="btn" on:click={save}>Save</div>
```

## Labelled input with help + error (3.3.1/3.3.2)

```html
<label for="email">Email address</label>
<input id="email" name="email" type="email" autocomplete="email" required
       aria-describedby="email-help" aria-invalid="true">
<p id="email-help">Used for order updates only.</p>
<p id="email-error" role="alert">Missing domain — try name@example.com</p>
```
input → `aria-describedby="email-help email-error"`, `aria-invalid` set from
validation state; server error map rendered, not injected.

## Dialog lifecycle (2.4.3 + focus return)

```html
<button id="open">Edit</button>
<dialog aria-labelledby="t">
  <h2 id="t">Edit record</h2>
  <!-- focus first field on open; Tab cycles here; Esc closes (native);
       focus returns to #open -->
</dialog>
```
`showModal()` handles trap+Escape. Return focus in the close handler for
custom flows. See `tooling/a11y-audit/fixtures/dialog.html` + scenario config
that audits this state open.

## Dynamic status (4.1.3)

```html
<p role="status" aria-live="polite">{saving ? 'Saving…' : saved ? 'Saved' : ''}</p>
```
mounted early, polite for routine, `role=alert` only for interruptions.

## CI gate (CI/CD snippet)

```yaml
- run: node path/to/skill/tooling/a11y-audit/bin/a11y.mjs audit \
    --config a11y.config.json --level aa --out a11y-report \
    --format json,html,junit --viewport both
# exit 1 blocks release on confirmed AA violations; AAA advisory separate
```

## Component keyboard test (Vitest+Playwright or Playwright CT)

```ts
test('dialog traps and restores', async ({ page }) => {
  await page.getByRole('button', { name: 'Edit' }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  for (let i = 0; i < 12; i++) await page.keyboard.press('Tab');
  await expect(page.getByRole('dialog')).toBeVisible();       // no trap leak
  await page.keyboard.press('Escape');
  await expect(page.getByRole('button', { name: 'Edit' })).toBeFocused(); // return
});
```
