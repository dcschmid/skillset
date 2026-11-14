# Dependency & supply-chain audit

Run `scripts/run-security-audit.sh deps <dir>` for the ecosystem inventory
+ fallback CVE surface; upgrade with real auditors per
`security-tooling.md` when installed. Direct AND transitive both in scope.

## Ecosystem dispatcher

| Lockfile present | Ecosystem | Auditor (probe) | Fallback here |
|---|---|---|---|
| package-lock / pnpm-lock / yarn.lock | npm | `npm|pnpm audit --json` | registry-free inventory + manual CVE lookup when online purpose stated |
| requirements.txt / uv.lock / poetry.lock / Pipfile.lock | python | `pip-audit` | inventory + pinned-version drift |
| Cargo.lock | rust | `cargo audit` | inventory |
| go.sum | go | `govulncheck ./...` | inventory |
| composer.lock | php | `composer audit` | inventory |
| *.csproj/packages.lock.json | dotnet | `dotnet list package --vulnerable` | inventory |
| Gemfile.lock | ruby | `bundle audit` | inventory |

## Assessment pipeline (per vulnerable package)

1. Package + installed version + advisory id (CVE/GHSA), direct vs transitive.
2. Fix available? smallest compatible patch version (current major only).
3. Reachable? vulnerable code path called from deployed entrypoints?
   (import graph / used API surface — cite it; unreachable ⇒ downgrade honestly)
4. KEV hit → active exploitation; EPSS ≥ 0.9 → elevated; both cite snapshot date.
5. Maintainer/build risk: install/postinstall scripts, provenance, lockfile integrity hashes.
6. Deploy risk: prod vs dev-only dependency (dev deps rarely BLOCK a prod release).
7. Verdict + severity via `risk-scoring.md`; fix class from `remediation-guidelines.md`.

## Supply-chain extras beyond CVEs

Typosquatting (near-miss names vs popular pkgs, unfamiliar authors) ·
dependency confusion (private scope vs public registry — check registries
per-scope) · install-script execution (pin + sandbox) · unpinned versions
(`^`/`latest` drift) · lockfile churn in diffs · CI caches poisoning builds ·
unreviewed lockfile diffs in PRs. Each: check exists only if ecosystem uses it.

## Remediation flow

```
advisory → target version → manager update (scoped: `npm i pkg@x.y.z`)
→ conflicts investigated → tests+build green → re-audit clean → changelog note
```
No major upgrades without approval. No lockfile deletion to silence audit.
No silent `--force`/`--legacy-peer-deps`. Registry config (private scopes)
preserved.

## No-safe-version exit

Document: affected versions, impact, mitigation in code (feature off,
parser sandbox, network egress list), owner, revisit trigger (patch
release). Status ≤ PARTIALLY FIXED. Never claim resolved.

## SBOM (optional, on request)

CycloneDX via `cdxgen` (js/py), `syft`, or `cyclonedx-py` when installed;
fallback: emit `sbom.cdx.json` bom-ref list from lockfile parse with a
`generated-by: heuristic` note — inventory ≠ vulnerability verdict.
