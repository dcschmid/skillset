# Audit and sync procedure

`scripts/docs_audit.py` collects evidence mechanically; this file is the
judgment layer around it. Both modes compare docs against PROJECT STATE, not
against templates.

## Audit loop (docs-audit /docs-audit)

1. **Inventory** — run `python3 scripts/docs_audit.py --json <root>`. It
   detects stack from manifests only (package.json/pyproject/Cargo/go.mod…),
   README answer coverage, env keys in samples vs docs, API surface signals,
   CI presence, secrets in docs.
2. **Read the named sources yourself** — scripts flag, agents decide. A
   "stale command" is confirmed by opening the manifest; never relay the
   script verdict as final truth without the file check when the fix edits.
3. **Tier every finding** — VERIFIED/DOCUMENTED findings become fixes;
   PLAUSIBLE become `open_questions`; UNKNOWN stays absent.
4. **Report** — verdicts PASS/WARN/FAIL/NOT RUN per check. Absent external
   tool (markdownlint, vale, lychee, redocly) = NOT RUN with the install or
   CI wiring named; never a simulated pass.
5. **Fix ladder** — edit only docs + clearly-owned docs tooling. Source-code
   bugs found on the way: report to the owning engineering skill, do not fix
   in a docs task unless asked.

## Sync loop (docs-sync /docs-sync)

`python3 scripts/docs_sync.py [--range main..HEAD] <root>` maps the git diff
to docs that must be re-read (routes→API docs, env→config docs, manifests→
install docs, CLI→reference). Output is a PLAN; edits happen only for facts
you re-verified against the changed source. No auto-rewrite of whole trees.

Drift table (source change → doc check):
routes/resolvers/proto/graphql → endpoints, methods, params, examples
migrations/models/schema → schema docs, field tables
.env/config samples → key, default, type in config docs
manifests/lockfiles → install/run/test commands, versions
Dockerfile/compose → ports, run order, prerequisites
CI/Makefile → required checks and build docs
cli/cmd/argparse/click/clap → flags and help text

## Gate policy

Docs release is not "validated" while any P0/P1 stands open. Report format:
counts per verdict + per-finding path:line + tier + proposed fix, so a human
or CI can re-run and diff.
