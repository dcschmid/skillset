# Example 10 — automated API contract tests

Task: "stop frontend breaking on response changes." Mode VERIFY (API lane).

CI steps: `validate-openapi.py openapi.yaml` (structure) on PR ·
`validate-openapi.py new --baseline released.yaml` breaking-diff (removed
fields/ops, new-required params) fail the build · consumer contract tests:
spec-driven (schemathesis or project-native snapshot of handlers vs schema)
on every handler · generated client build = release gate; drift blocks.
Drift found in run: handler returned `total_count`, spec had `total_count?`
optional → code fixed to spec or spec versioned+deprecation header
(Sunset); never silently patched by weakening the schema.
