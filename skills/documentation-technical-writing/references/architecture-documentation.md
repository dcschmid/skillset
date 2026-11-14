# Architecture documentation

Real components or nothing. Every box exists in the tree; every edge is a
call/config/deploy relation you read somewhere.

## Tool choice

- Mermaid: default — versionable, renders on GitHub and most doc platforms.
  Verify the target renderer supports the diagram type before writing
  (GitHub: flowchart/sequence/state/C4-ish via flowchart; PlantUML needs a
  renderer/plugin).
- PlantUML/C4: when the project already ships one — extend its style.
- Generated (mmdc/plantuml CLI): wire into docs build so diagrams stay true.

## Content contract (ARCHITECTURE.template.md)

overview prose → component table (path, role, deps from imports/config) →
primary data flow → trust boundaries (from middleware/config) → deployment
(from Dockerfile/compose/CI). Each unverifiable area → Open questions.

## ADRs (docs/adr/NNN-slug.md, assets/ADR.template.md)

Only real decisions: commit history, tickets, code comments as context.
Status transitions reference each other (supersedes/superseded-by). Missing
history → mark "reconstructed, rationale unconfirmed", never invent a
decision narrative. Numbering: next free integer, kebab slug.

## Diagram hygiene

No gradient art, no decorative clouds, boxes = deployables/modules at the one
abstraction level the reader needs. When two abstraction levels are needed,
two diagrams. Verify Mermaid parses when mmdc/renderer exists; else state
renderer-unverified (NOT RUN).

Overlap: code-quality skill provides verified architecture *analysis* —
consume its output as evidence; this skill owns the written artifact.
