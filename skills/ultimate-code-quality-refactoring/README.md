# Ultimate Code Quality & Refactoring

Audit-first, verify-always skill for improving existing codebases without
silent regressions. Language-agnostic; edits only in explicit fix modes;
every claim traces to a `file:line` or a measured number.

## Tasks

technical debt · code smells · duplication · complexity · dead code ·
architecture/boundaries · perf hypotheses · type/error-handling consistency ·
modularity · safe refactoring · baseline comparisons · pre-merge gates.

## Requirements

- Python 3.8+ on PATH (scripts are stdlib-only, no installs).
- Optional external tools (ast-grep, jscpd, Sonar, OpenRewrite, ts-morph,
  language linters) are used only when the project already ships them —
  presence-probed, version-checked. Missing tools → UNVERIFIED entries.
- Git repo for change-safety features; non-git dirs still audit fine
  (change surface reported as unknown).

## Install / activate

Repo convention: symlinked by `tools/install-skills.sh` into
`~/.claude/skills` (Claude Code) + `~/.agents/skills` (Codex); oh-my-pi
loads both roots — nothing extra per skill. Invoke by name:

```text
Use the ultimate-code-quality-refactoring skill: audit packages/core for
complexity hotspots and dead code; PASS/FAIL/UNVERIFIED only, no invented scores.
Use the ultimate-code-quality-refactoring skill: refactor the pricing module
without changing behavior — baseline, per-step verify, evidence report.
```

## Modes & invocation

AUDIT (default, read-only) · QUICK AUDIT · SAFE AUTOFIX · DEEP REFACTOR ·
ARCHITECTURE REVIEW · DEBT CLEANUP · PRE-MERGE GATE · CONTINUOUS QUALITY.
Trigger in natural language ("Führe einen vollständigen Code Quality Audit
durch", "Refaktoriere dieses Modul, ohne Verhalten zu verändern",
"Behebe sichere Code Smells und teste anschließend") or with the
`/quality-*` shorthands (`/quality-audit`, `/quality-fix`,
`/quality-refactor`, `/quality-architecture`, `/quality-debt`,
`/quality-verify`). Slash-less agents: use the phrases.

## Quick start

```bash
S=skills/ultimate-code-quality-refactoring/scripts
python3 $S/run_audit.py PATH/TO/PROJECT -o /tmp/qa        # AUDIT bundle
python3 $S/generate_report.py /tmp/qa/quality-audit.json  # Markdown report
# fix modes (only after baseline exists):
python3 $S/verify_changes.py PATH -o /tmp/base.json --save-baseline --cmd "npm test"
python3 $S/verify_changes.py PATH --baseline /tmp/base.json --cmd "npm test"
```

## Safety rules (summary)

User's uncommitted work is never overwritten; no commits/pushes/installs
without being asked; HIGH-risk changes need approval; revert = own hunks
only; existing failures stay baseline; absent tools documented, results
never simulated. Details: `references/safety-and-rollback.md`.

## Testing workflow & quality gates

Per-step: syntax → lint → typecheck → affected tests → suite → baseline
compare. Gates: no NEW failures, no unintended API change, no new P0/P1,
no hidden behavior diff, no measured perf regression. `verify_changes.py`
exit 0=PASS, 1=FAIL, 2=UNVERIFIED.

## Report formats

`assets/audit-report.md`, `assets/refactoring-plan.md`,
`assets/technical-debt-backlog.md`, `assets/before-after-report.md` —
rendered by `generate_report.py` / `compare_baseline.py` from measured data.

## Integrations

ultimate-testing-qa (regression runs), ultimate-security-hardening (deep
security pass on changed areas), accessibility/seo-performance (UI surfaces),
astro/react-nextjs/defold-development/godot (engine verification). Contract:
hand over changed-file list + baseline; absent skills change nothing (this
skill stays standalone).

## Known limits

Complexity numbers are labeled proxies without a language compiler; clone
detection is token-window based (candidates only); behavior proof beyond the
project's executed checks stays UNVERIFIED; semantic refactoring needs the
language's own tooling when edits exceed textual safety.

## Updating for new frameworks/tools

Add rows to `references/language-adapters.md` / `tool-integration.md`
(presence-gated tables) and, if needed, per-language tables in
`scripts/collect_metrics.py` (`CODE_EXTS`, `BRANCH_WORDS`). No pinned
versions anywhere; probe live versions at task time. After edits run
`python3 tests/test_skill.py`.
