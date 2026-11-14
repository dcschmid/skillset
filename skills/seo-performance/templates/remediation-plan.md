# Remediation Plan — {{name}}

Priority order: severity → impact → diagnosis confidence → effort → regression risk.

| # | finding | sev | URL/file | probable cause | fix | effort | risk | approval | verify |
|---|---|---|---|---|---|---|---|---|---|
| 1 | {{id}} | {{sev}} | {{url}} | {{cause}} | {{fix}} | S/M/L | low/med/high | auto|manual | {{verifyCmd}} |

## Workflow per fix (all fixes, no exceptions)
1. Baseline snapshot exists (`latest.json` before the change).
2. Fix at root cause, framework-native where the framework provides it.
3. Build → tests → re-audit → `compare` old vs new snapshot.
4. Diff reviewed (`git diff`); result documented whether it helped or not.

## Needs explicit approval (never auto-applied)
- redirect migrations, canonical rewrites, content removal,
- architecture/framework changes, dependency additions.

## Verification commands
```bash
node scripts/seo.mjs audit <target>            # re-audit
node scripts/seo.mjs compare <before> <after>  # noise vs regression
```
