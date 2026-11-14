# Workflow: ANTI_AI_SLOP_CLEANUP

Targeted sweep against generic AI patterns in an existing project. Narrower
than AUDIT_AND_FIX: only slop findings, only proven-in-context fixes.

1. **Scope + discovery** (`project-discovery.md`), browser probe as in AUDIT.
2. **Detect** `anti-ai-patterns.md` A–J: unmotivated gradients, unjustified
   glassmorphism, glow, interchangeable hero sections, repetitive feature
   cards, default SaaS layouts, arbitrary decoration (blobs/circles),
   purposeless icons, card nesting, missing identity, generic content
   presentation. Rendered evidence where possible.
3. **Filter — only project-proven problems.** Classification filter binding
   (`anti-ai-patterns.md`): deliberate style / constraint / taste are NOT
   removed. A gradient that is the brand stays; the card grid that is correct
   stays. Removal or rework only when THIS product's context shows it hurts.
4. **Fix** per `safe-auto-fix.md`: tokens/components first, smallest diffs,
   content facts untouched (copy rework → Human-Writing capability if present;
   else propose text, apply only UI microcopy in scope).
5. **Verify + report:** detection re-run on touched surfaces = clean or logged
   nits; visual regression pairs; score delta only from real renders; report
   `audit-report-format.md` scoped to cleanup findings.
