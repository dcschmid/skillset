# Security standards registry (probe before citing)

Verified 2026-11-14 against official OWASP/NIST/MITRE/CISA/FIRST sources.
Stable = publishable baseline; Draft/RC = label explicitly, never silently
mix into findings. Re-verify on every skill update; link + version per row.

| Standard | Version | Status | Official source |
|---|---|---|---|
| OWASP Top 10 | 2025 | Stable | https://owasp.org/www-project-top-ten/ |
| OWASP ASVS | 5.0.0 | Stable | https://owasp.org/www-project-application-security-verification-standard/ |
| OWASP API Security Top 10 | 2023 | Stable | https://owasp.org/www-project-api-security/ |
| OWASP WSTG | 4.2 | Stable | https://owasp.org/www-project-web-security-testing-guide/ |
| OWASP Cheat Sheet Series | rolling | Stable (rolling) | https://cheatsheetseries.owasp.org/ |
| MITRE CWE | rolling | Stable | https://cwe.mitre.org/ |
| CWE Top 25 | 2025 list | Stable | https://cwe.mitre.org/top25/ |
| NIST SSDF (SP 800-218) | 1.1 | Stable | https://csrc.nist.gov/pubs/sp/800/218/final |
| CISA KEV Catalog | rolling | Stable (rolling) | https://www.cisa.gov/known-exploited-vulnerabilities-catalog |
| FIRST EPSS | rolling | Stable (rolling) | https://www.first.org/epss/ |
| CVSS | 4.0 (3.1 legacy) | Stable | https://www.first.org/cvss/ |
| OWASP CycloneDX | 1.6 spec | Stable | https://cyclonedx.org/ |

## OWASP Top 10:2025 — full coverage map (audit MUST cover all ten)

| ID | Category | Audit module (audit-modules.md) | Primary CWE family |
|---|---|---|---|
| A01 | Broken Access Control | §B Authorization | CWE-284/639/862/863 |
| A02 | Security Misconfiguration | §I Config Hardening | CWE-1188/16 |
| A03 | Software Supply Chain Failures | dependency-security.md | CWE-829/937/1104/471 |
| A04 | Cryptographic Failures | §H Cryptography | CWE-326/327/324/312 |
| A05 | Injection | §C Injection + §D XSS | CWE-89/77/79/502/611 |
| A06 | Insecure Design | threat-model.md | design-level (SSDF PW/PS) |
| A07 | Authentication Failures | §A Authentication | CWE-287/384/521/613 |
| A08 | Software or Data Integrity Failures | deps + CI/CD + §H | CWE-345/353/502 |
| A09 | Security Logging & Alerting Failures | §J Errors/Logging | CWE-778/1009 |
| A10 | Mishandling of Exceptional Conditions | §J Errors/Logging | CWE-703/754/248 |

## ASVS 5.0.0 usage

ASVS is the verification requirement set: each audit module maps to ASVS
chapters (V2 auth, V3 config, V4 crypto, V5 input validation, V6 errors
& logging, V7 data, V11 business logic, V14 files, V18 mobile, etc. — read
the live TOC, chapter numbering changed across versions). Use ASVS levels
as depth dials: L1 = quick audit, L2 = full audit, L3 = critical systems.

## WSTG 4.2 usage

WSTG supplies the test methodology: information gathering → configuration
→ auth → session → input validation → error handling → weak crypto → code
quality → business logic → client-side. Each audit step cites its WSTG
section ID in the report when available so a reviewer can extend checks.

## Version discipline rules

1. Cite standard version + access date in the report header.
2. Draft/rc standards (e.g. future OWASP releases) get a `DRAFT` tag and
   NEVER block a release gate on draft-only requirements.
3. CWE/KEV/EPSS are rolling — cite the snapshot date, not "latest".
4. When re-verifying: fetch the official page, compare table above, update
   row + probe date. Never update from blog summaries.
