# Orchestration and dependency graph

## Graph sources (real data, not example chains)

- explicit edges: `metadata.dependencies`, the phrases requires X skill /
  depends on X skill found in descriptions and bodies.
- collaboration edges: cross-mentions between skill texts (undirected).
- layers: keyword classification per skill — coordinate, implementation,
  asset-pipeline, audit, verification, content.
- conflicts: contradictory instructions (verified quotes only).

The example chains below are what the graph happens to produce for two
task families on THIS repository. They are outputs, never hardcoded
orders; `plan` derives order from layer rank + explicit deps.

Website task (astro + a11y + seo + tests):

    implementation(astro) → audit(accessibility, seo-performance)
    → verification(ultimate-testing-qa)

Game task (godot + 3D assets):

    implementation(godot) → asset-pipeline(lowpoly-reference-to-blender
    only when 3D assets are in scope) → verification(godot tests /
    project runner)

Quality gates between steps are emitted only when the selected skills
imply them (a11y PASS != conformance; security confirm-before-fix;
perf lab-vs-field; functional test gate). Duplicate gates are deduped;
independent same-layer steps may run in parallel; the orchestrator does
not re-implement any domain check itself.

## Graph health checks (overlap command + audit)

- cycles: DFS over explicit edges only; reported as a -> b -> a chains.
  Current collection: none.
- missing targets: dependency phrases naming skills that do not exist.
- stale catalog entries: snapshot skills absent from a fresh scan.

## Recursion limit

`audit`/`overlap` treat skill files as data. The orchestrator audits its
own SKILL.md (skill-orchestrator appears in catalog and audits) but never
launches itself recursively: no CLI command spawns another CLI process;
agent-evals spawn an agent CLI once, in a temp dir, and stop.