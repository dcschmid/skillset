# Platform Adapters

Platform-independent core (`scripts/harness_lib.py`) + thin adapters. An
adapter maps platform truth ⇄ portable contract; it never weakens checks and
never invents APIs. Verify capability on the host before claiming it.

## Adapter contract

1. Probe: what does this host actually expose (tool manifest format, tool
   protocol, permission model, state store, trace/metrics source)?
2. Map: platform value → portable contract value; unmapped = reported, not
   defaulted.
3. A valid platform-specific field (e.g. a host enum) is a platform truth —
   the audit reports it as such, never rewrites it.

## Capability matrix (verify per install; rows are the questions to ask)

| Platform | Tool manifest | Protocol | Permissions | State | Traces/metrics |
|---|---|---|---|---|---|
| Claude Code | skills dir + settings allowlists | host-native tool calls + MCP | allow/deny lists, sandbox, `--` prompts | files, memory dirs | session logs (check version) |
| OpenAI Codex | AGENTS.md + config | function-calling style | sandbox modes | files | session output (check version) |
| Open WebUI | function/pipeline plugins | python-function schema | per-model settings | chat history | UI logs (limited) |
| own Python agent | your code = truth | yours (define observation shape) | yours | yours | emit trace JSON for these tools |
| own TS agent | same as Python | same | same | same | same |
| MCP-based | tool schema JSON-RPC | MCP (spec version pinned) | server-side | server-side | MCP sampling/logging (check server) |

Undocumented/absent capability on a host ⇒ document as unsupported for that
host. Slash commands, env names, and file locations are only documented where
their support is verified on the machine in use.

## Trace interop

Every host ultimately can emit: `{"steps": [{kind, name, arguments, ok}]}` —
the minimal shape detect_loops/analyze_traces/benchmark offline consume.
Adapter = the 10-line function translating host events to that shape. Host
can't emit events ⇒ benchmark stays offline over whatever artifacts exist and
says so.
