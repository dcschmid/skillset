# seo-performance

Audit technical SEO, metadata, structured data, and web performance. Distinguish delivered HTML from rendered DOM and lab results from field data.

Profile: Private and Working. Preparation: Provide the URL or project path and affected pages. Use comparable conditions for performance measurements.

Expected result: Prioritized findings with evidence, authorized fixes where applicable, and before-and-after checks.

Requirements and limits: Keep measurements separate from estimates. Local lab results do not replace field data. Apply fixes within the skill rules and the scope already authorized.

## seo-performance: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh seo-performance
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the seo-performance skill. Audit the published site for canonicals, robots.txt, sitemap, and structured data. Identify the specific URLs affected.
```

**Codex:**

```text
Use the seo-performance skill. The home page has poor LCP. Measure under comparable conditions, find the cause, and verify the effect of a focused fix.
```

**oh-my-pi:**

```text
Use the seo-performance skill. Check the rendered output in the existing build directory for missing titles and conflicting metadata. Produce a report first.
```

## seo-performance: Self-test

Run from the repository root:

```bash
node skills/seo-performance/tests/run.mjs
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [templates/](templates/): Templates for the target project.
- [examples/](examples/): Worked examples.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [seo.mjs](scripts/seo.mjs)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/seo-performance` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
node scripts/seo.mjs tools
node scripts/seo.mjs audit /path/to/project
node scripts/seo.mjs technical /path/to/project
```

## Interpret audit evidence

`seo.mjs tools` lists available measurement tools. Pass a real URL instead of
a directory for a URL audit. Source inspection, built-output checks, and
measurements on the published site provide different evidence; report the
context of each result.
