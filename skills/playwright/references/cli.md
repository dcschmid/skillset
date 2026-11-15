
Use the wrapper script (`scripts/playwright_cli.sh`) unless a Playwright CLI is
already on PATH — it resolves `$PLAYWRIGHT_CLI`, then `playwright-cli`, then a
repo launcher, and installs nothing itself:

export PWCLI="$PWD/scripts/playwright_cli.sh"
"$PWCLI" --help
```

Optional convenience alias:

```bash