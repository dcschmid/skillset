# Sibling-skill integration (collection-specific)

Detected from installed skills; absent skills change nothing — the review
runs standalone. Delegation is one-way: this skill calls out, callers never
call back (recursion guard).

| axis | delegate when present | hand back |
|---|---|---|
| security | `ultimate-security-hardening` (deep audit, dep CVEs, secrets) | schema findings, axis `security` |
| standards/perf | `ultimate-code-quality-refactoring` (dupes, complexity, debt) | schema findings, own axes |
| testing | `ultimate-testing-qa` (run suites, coverage gaps) | executed-check results |
| UI/UI-a11y diffs | `accessibility`, `design-system-ui` | a11y findings |
| web per-stack | `react-nextjs`, `astro`, `backend-api-engineering`, `seo-performance` | stack findings |
| game per-engine | `godot`, `defold-development`, `lowpoly-reference-to-blender` | engine findings |
| docs in diff | `documentation-technical-writing` | doc findings |
| CI diffs | `ci-triage` / `semgrep-security` | pipeline/scan findings |
| PR comments | `review-followup` (that skill posts, this one never does) | — |

Rules: reuse a fresh result over rescanning (`a prior ultimate-* report on
the same SHAs is evidence, cite it`); never claim an integration ran for a
skill that isn't installed; orchestrator (`skill-orchestrator`) audits the
collection, not a review's verdicts.
