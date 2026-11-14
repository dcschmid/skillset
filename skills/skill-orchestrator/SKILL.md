---
name: skill-orchestrator
description: >
    Central quality and orchestration manager for this skillset repository.
    Use when asked to discover, inventory, validate, audit, score, route,
    overlap-check, test, repair, or report on the skills themselves, or to
    plan which skills serve a task ("which skills for an accessible Astro
    site?", "audit my skill collection", "is skill X valid?"). Runs a
    deterministic Python 3 CLI over real files — discovery never invents,
    scoring never credits unchecked areas, agent-evals report UNAVAILABLE
    instead of fake passes. Read-only by default; repairs are proposals
    until you approve. Coordinates other skills; it does not duplicate
    their domain expertise.
---

# Skill Orchestrator & Validator

Manages the collection, never the domains: framework/engine/audit skills
own their expertise; this skill owns discovery, validation, routing plans,
overlap truth, quality scores, regression tracking, and safe repair.

## Activation

Activate for questions about the skill collection itself. Do NOT activate
for ordinary development tasks — those route directly to domain skills
(the orchestrator's routing engine answers "which skill?" only when asked).

## Setup (once)

CLI lives at `scripts/skill-orchestrator` (executable, stdlib Python 3.10+;
PyYAML optional, built-in fallback parser keeps it functional without).
Run from anywhere — repo root is auto-detected (`SKILL_ORCHESTRATOR_ROOT`
overrides):

```bash
skills/skill-orchestrator/scripts/skill-orchestrator doctor
```

## Workflow spine (read-only first)

1. `scan` → skill-catalog. New skills appear without registration;
   symlinks resolved, cycles and broken links skipped, duplicates reported.
2. `audit --all` → per-skill 100-point score, 7 categories, tiered findings
   (`standard`/`host`/`repo`/`unknown` — a valid Claude field is never a
   portable error). Unchecked = 0 credit, marked, never guessed. Blockers:
   security errors or invalid required metadata cap the grade regardless
   of points.
3. `route "<task>"` → auditable plan: selected skills + reasons + order +
   dependencies + gates + rejected-and-why. Plan only; changes nothing.
   Engine skills are exclusive (godot ≠ defold); frameworks are not
   force-migrated (react stays react under an astro question).
4. `overlap` → cooperation / partial / problematic / conflict, every verdict
   with file+line evidence. Similarity scores are signals, never proof.
5. `test --all` → static, routing, conflict, integration tiers run for real.
   `eval --skill X` runs a behavior eval through an installed agent CLI;
   without one it reports UNAVAILABLE — fabricated passes are forbidden.

Only then, with approval:

6. `fix --skill X` (dry-run diff) → `--apply` after review; minimal edits,
   git-revertible, re-run `audit --skill X` to catch regressions.
7. `audit --all --save` stores the snapshot; later audits report
   score/error regressions and collection deltas automatically.

## Gates

- Discovery facts come from files; quality claims require the audit run.
- A score is not a test result; report both or neither.
- Repairs: propose → approve → apply → regression-check → targeted rollback on failure. Before editing, preserve the original contents
  of affected files (including uncommitted work). Undo only this run’s edits;
  never use whole-file checkout/reset to discard pre-existing changes. If
  concurrent edits prevent a safe rollback, retain them and report the conflict.

Rule tables: [references/validation.md](references/validation.md) ·
routing: [references/routing.md](references/routing.md) ·
scoring: [references/quality-scoring.md](references/quality-scoring.md) ·
graph: [references/orchestration.md](references/orchestration.md) ·
profiles×hosts: [references/compatibility.md](references/compatibility.md).
CLI details: [README.md](README.md).
This SKILL.md is the router; depth is one hop away, per repository law.