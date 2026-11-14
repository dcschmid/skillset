# Workflow: AUDIT (existing projects, zero code changes)

Full or selective analysis of an existing project. Output = report, no edits.
An audit never auto-escalates into fixes; fixes belong to AUDIT_AND_FIX on task.

1. **Project Discovery** — `references/project-discovery.md` (read-only): stack,
   tokens, routes, tooling, conventions, runnability. Selective scope from the
   request (whole/route/page/component/viewport/theme/changed-files) stays the
   scope; big project → sampled routes, coverage stated.
2. **Render what runs.** Browser available (project's own or the accessibility
   skill's Playwright) → screenshots of representative routes × viewports ×
   themes × states (nav, forms, dialogs, menus, hover, focus, loading, error),
   inspected FOR concrete problems, not collected blindly. No browser →
   documented source/structure fallback; never claim a visual pass.
3. **Audit categories** A–H: authenticity (`anti-ai-patterns.md` A–J),
   typography (`typography.md` checks), color, layout, components
   (`design-principles.md`), UX (guidance, feedback, empty/loading/error,
   mobile nav), accessibility (delegated: `accessibility` skill +
   `accessibility-integration.md` floors; automated + manual queue), visual
   quality (overflow, broken wraps, unreadable text, imbalance — from renders).
4. **Cross-page consistency** (`anti-ai-patterns.md` J across routes): headers,
   buttons, spacing, type sizes, cards, duplicated tokens, color conflicts,
   forms, sibling-route navigation drift. Deliberately different page types
   stay different; central fixes at shared-source level.
5. **Content credibility** (when design-affecting): generic hero/CTAs, filler,
   repetitive blocks, placeholder text. Facts/prices/legal/published content
   are read-only unless tasked; editorial rewrite → delegate to a Human-Writing
   capability when one exists in the project's skill set.
6. **Score + report.** `visual-quality-gates.md` rubric before-column;
   `audit-report-format.md` → `reports/design-authenticity-audit.md`.
   Missing prerequisites → transparent NOT AVAILABLE/NOT TESTED lines.
