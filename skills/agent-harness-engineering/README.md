# agent-harness-engineering

Audit tools, observation formats, context budgets, error handling, loops, and agent coordination. Python tools analyze real configurations and recorded traces.

Profile: Private and Working. Preparation: Provide the harness directory, tool definitions, and traces or benchmarks for runtime questions.

Expected result: An evidence-backed audit, contract validation, or comparison that distinguishes recorded data from live measurements.

Requirements and limits: Unobservable areas remain UNVERIFIED or are skipped with a reason. Label offline benchmarks as offline. Use skill-orchestrator for choosing skills for a product task.

## agent-harness-engineering: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh agent-harness-engineering
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the agent-harness-engineering skill. Audit our agent harness for duplicate tools, swallowed errors, and unbounded retries. Start with an evidence-backed report.
```

**Codex:**

```text
Use the agent-harness-engineering skill. Analyze trace.json for repeated identical tool calls. Identify the steps and propose a bounded retry strategy.
```

**oh-my-pi:**

```text
Use the agent-harness-engineering skill. Compare stored benchmarks before and after the tool change. Report regressions and label the comparison as offline.
```

## agent-harness-engineering: Self-test

Run from the repository root:

```bash
python3 skills/agent-harness-engineering/tests/test_skill.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [assets/](assets/): Support files and templates.
- [examples/](examples/): Worked examples.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [analyze_context.py](scripts/analyze_context.py)
- [analyze_traces.py](scripts/analyze_traces.py)
- [audit_harness.py](scripts/audit_harness.py)
- [benchmark_agent.py](scripts/benchmark_agent.py)
- [compare_benchmarks.py](scripts/compare_benchmarks.py)
- [detect_loops.py](scripts/detect_loops.py)
- [generate_report.py](scripts/generate_report.py)
- [harness_lib.py](scripts/harness_lib.py)
- [security_scan.py](scripts/security_scan.py)
- [validate_observations.py](scripts/validate_observations.py)
- [validate_tools.py](scripts/validate_tools.py)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/agent-harness-engineering` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
python3 scripts/audit_harness.py --project /path/to/project --format markdown
python3 scripts/validate_tools.py /path/to/tools.json
python3 scripts/detect_loops.py /path/to/trace.json
```
