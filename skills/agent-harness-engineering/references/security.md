# Agent Security

Machine check: `scripts/security_scan.py`. Risk model shared with all scripts:
**LOW** (read-only, local) → **MEDIUM** (reversible edits in project) →
**HIGH** (config/external writes/production) → **CRITICAL** (destructive,
irreversible). HIGH+CRITICAL need explicit approval; dry-run never writes.

## Prompt injection surface

Direct (user text) is cheap to handle; the real surface is **indirect**:
tool outputs, documents, web pages, repo files, inter-agent messages. Control:
external content enters as *data* — wrapped, attributed, never concatenated
into the instruction channel. An instruction that arrived via a tool result is
information to evaluate, not a command to obey. Every observation the harness
prints is untrusted input to the next step.

## Tool security

Least privilege per tool: enumerate `allowed_paths`, bound `timeout_ms`,
declare `idempotent`, allowlist tools per agent instead of `"*"`. Shell
execution: no bare shell strings — argv arrays, timeout, output caps, cwd
pinned. Path handling: resolve, then containment-check against the project
root before use (traversal). Network: explicit hosts, no ambient credentials.

## Secrets

Source: env/secret store, never literals in prompts, instruction files, or
traces. Logs/traces mask before write (analyze_traces.py redacts on output).
Config files with credentials get the same protection class as the secret.

## Execution

Sandbox where the host offers one (host sandbox, container, restricted cwd);
resource limits and timeouts always; defaults conservative; actions auditable
via trace + correlation id. No self-escalation: an agent never widens its own
permissions mid-task — widening is a HIGH operation issued to the owner.

## Adapter obligations

Platform adapters (platform-adapters.md) may map vocabularies but MUST NOT
weaken checks: a platform enum value that is valid there is reported as a
platform truth, not a portable error — and never auto-"fixed".
