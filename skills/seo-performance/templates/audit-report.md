# SEO & Performance Audit — {{name}}
_captured {{capturedAt}} · framework: {{framework}} ({{rendering}}) · pages: {{pagesMeasured}}_

## Management Summary
{{managementSummary}}

## Executive Summary
| severity | count |
|---|---|
| critical | {{counts.critical}} |
| high | {{counts.high}} |
| medium | {{counts.medium}} |
| low | {{counts.low}} |

**Data gaps:** {{dataGaps}}

## Technical SEO
{{technicalSeo}}

## Performance
| metric | value | threshold | source | verdict |
|---|---|---|---|---|
<!-- rows only from measurements; missing => "not measured" -->
{{performanceTable}}

## Findings & Remediation Plan
| ID | sev | category | URL/file | evidence | probable cause | fix | effort | risk | verify |
|---|---|---|---|---|---|---|---|---|---|
{{findingsTable}}

## Before / After (only when both snapshots exist)
{{compareTable}}

_Management summaries and scores are lab measurements, not ranking guarantees. INP is a field metric; only CrUX/RUM values are reported._
