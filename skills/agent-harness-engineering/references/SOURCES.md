# Sources & attribution

Concepts in this skill build on, and extend, the **ECC
`agent-harness-construction` skill** (Affaan Mustafa, MIT-licensed — see
upstream `LICENSE`): action-space/observation/recovery/context-budget quality
model, micro/medium/macro tool granularity ladder, observation response
shape, error-recovery contract, phase-boundary compaction, benchmark metric
set, anti-pattern list. This skill is an independent reimplementation with
working validators, not a copy.

Further references (specifications/docs consulted for vocabulary only):

- Model Context Protocol specification — tool schema + JSON-RPC vocabulary
  (platform-adapters.md capability rows).
- OpenTelemetry traces vocabulary (trace/span/correlation) in
  references/observability.md — concepts adapted, no runtime dependency.
- JSON Schema draft-07 — subset validator in `scripts/harness_lib.py`
  (`validate_schema`); unknown keywords ignored, never invented.
- MCP/OTel/EVAL docs are linked as documentation; no code was copied from
  them. ECC prose was likewise not copied — every file here is new text
  implementing the concepts with machine checks added.

MIT attribution: Copyright (c) 2026 Affaan Mustafa — permission granted by
upstream MIT license; retain this notice where redistributed.
