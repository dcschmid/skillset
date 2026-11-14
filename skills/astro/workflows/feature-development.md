# Workflow: Feature Development (page, section, or capability)

Applies: additive work on an existing site (new page, form, search, feed,
gallery, i18n slice, dashboard block).

1. **Define done**: route(s), data source, interaction level, design input,
   SEO needs. One paragraph; ambiguous → smallest reversible assumption.
2. **Locate the seam**: layout/component to reuse, collection to extend,
   action to add (existing-project.md conventions apply).
3. **Choose the interactivity rung** (islands-interactivity.md ladder):
   HTML/CSS → inline script → server island → client island — first rung that
   satisfies; record the rung + reason.
4. **Implement**: pages thin, data behind lib/collection (architecture.md);
   typed props/actions; tokens for visuals; content schema first if data is
   involved (templates/content-collection.md).
5. **SEO/a11y on the new surface**: head props, structured data if a document
   type; authored-in a11y checks (accessibility.md).
6. **Verify**: check → build → preview the new routes + one neighbor
   (no regression); MEASURED: bundle delta for new islands
   (`du dist/_astro`), lighthouse if perf-sensitive; feature test where the
   repo has a test lane.
7. **Report**: routes added, decisions, verification table, follow-ups.
