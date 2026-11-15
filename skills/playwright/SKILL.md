---
name: playwright
description: >
    Automate a real browser from the terminal for UI exploration, navigation,
    snapshots and interaction debugging. Triggers on "open this page", UI
    reproduction, screenshot evidence, and manual-flow debugging.
---
# Browser automation with Playwright

Use an installed Playwright CLI (official `playwright-cli` or the repository's
own browser tooling). Default to Firefox unless the repository pins another
browser; keep one browser session per project and purpose so parallel agents
never share page state. Repository browser settings and explicit user choices
take precedence.

If no CLI is available, use an existing repository Playwright workflow or
explain the missing runtime. Do not install a second global CLI merely because
this skill is present.

Prefer existing repository regression tests when they cover the requested
behavior. Use terminal automation to inspect a UI or reproduce interactions;
it does not replace the project's test suite. Add test files when they
materially verify a requested behavior change.

```bash
playwright-cli open http://localhost:4321
playwright-cli snapshot
# Use a real element reference from the returned snapshot:
playwright-cli click e15
playwright-cli snapshot
```

Read fresh snapshots before using element references, and refresh after
navigation, dialogs or significant DOM changes. Verify interaction state and
browser errors as well as screenshots. Use traces for a difficult
reproduction and retain artifacts in the repository's existing output
location, or `output/playwright/`.

Do not reuse personal browser logins across unrelated projects. Preserve
session separation between projects and profiles; avoid reusing session names
across unrelated tasks. Stateful submissions and external account actions must
stay within the user's authorized scope. Never report an unrun browser check
as passed.

For detailed CLI syntax, read [the command reference](references/cli.md). For
navigation, snapshots, forms, dialogs and traces, read
[workflow examples](references/workflows.md) only as needed. Confirm flags
against the installed CLI when references and runtime differ.
