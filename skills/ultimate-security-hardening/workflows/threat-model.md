# Workflow: threat-model (design-time + audit-time)

Output drives audit priorities and business-context severity. Full form for
critical systems; condensed (steps 1-3 in 60s) inside quick audits.

## 1 Inventory (from detect-project.sh)
Entry points (routes, forms, CLI args, file uploads, WS, webhooks, CI
triggers, admin UI) · data stores · services · external callers · secrets
locations · dep boundaries (direct/transitive, registries).

## 2 Trust boundaries (the sentence that makes audits honest)
Name each: browser→API · CI-token→repo · build-script→machine ·
config-file→runtime · user-content→renderer · transitive-dep→app ·
partner-webhook→handler. Everything crossing gets validation at the
boundary — that's Zero Trust operationalized, and where findings rank higher.

## 3 Data flows + sensitivity map
For each store: what's PII/credential/money/tenant-scoped, who may read,
where it's serialized (logs? client? cache?). Leaks here = CRITICAL context.

## 4 Abuse paths (per entry point, attacker = anon / legit-user-A /
compromised-dep / rogue-CI)
- skip authz by calling internal endpoint directly? enumerate ids?
- overflow: unbounded lists/uploads/queries (availability + cost)
- inject where output later renders/stores/queries
- replay: webhooks/tokens/reset-links
- deserialization/parsing of "trusted" upstream (partner, cache, file)
- dep confusion/typosquat in registries the build hits

## 5 Existing controls inventory
Framework escaping · gateway/proxy authz · middleware order · WAF · typed
schemas · CI caching. Downgrades per risk-scoring.md need a named control.

## 6 Miss analysis → audit brief
Per OWASP Top 10:2025 (map in security-standards.md) assign: covered-by
(module), partially, or gap. Gaps = module run order + severity context
for PRIORITIZE. Insecure design gaps (A06, SSDF PW) may only be answerable
by design change — surface as RECOMMENDATION, not a code fix.

## 7 Output artifact
`security-reports/threat-model.md` per templates/ spirit: boundary diagram
(text), data map, abuse-path table, module-order + severity context.
Feeds FULL AUDIT step 2; re-verify when architecture shifts.
