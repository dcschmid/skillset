# Website rewrite (Mode E) — 8 phases, protected spans, approval gates

Local projects: `scripts/project_audit.py`. Remote: audit report is the
deliverable; copy-ready blocks for the maintainer. Never touch production
CMS/deploy APIs without explicit approval; never destructive git commands.

**Discover** → pages, language, source location, project vs URL-only.
**Extract** → prefer original files (md/mdx/astro/tsx/json content) over HTML.
**Analyze** → full audit (`website-audit.md`); findings per element.
**Rewrite** → agent authors replacements: facts intact, no invented content,
voice per `website-voice.md`, keywords that belong stay, length fits the slot.
**Compare** → original vs new vs reason per change; missing facts flagged,
never filled.
**Approve** → modes: audit-only / proposals / per-change / all / direct-edit
(direct requires explicit instruction). Default: dry run.
**Apply** → `project_audit.py plan|apply`; protected regions untouched
(code fences, frontmatter, JSX expressions, imports, ARIA, hrefs, slugs,
canonicals, structured data, ICU/templating vars, translation keys). No
regex-sweep of JSX/TSX; if unsure, emit a manual patch instead.
**Validate** → build + tests + typecheck via `validate --build/--test`;
links, meta, structure re-checked. Errors: fix or revert that edit; never
continue over failures.

Patch JSON: `{proposals:[{file,span:[start,end],original,replacement,reason,approved}]}`
— `apply` verifies `original` still matches before writing.

## Honest limits

Python here detects, plans, validates, applies approved diffs. Productive
rewriting is the agent's; do not present script output as editorial prose.
