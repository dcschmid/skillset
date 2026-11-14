# Ultimate i18n & Localization Audit

Project: {{project}}
Stack: {{stack}} · system: {{system}} · engine: {{engine}}
Reference locale: {{reference}} · locales: {{locales}}
Locales dir: {{localesDir}}
Coverage: {{#coverage}}{{locale}} {{percent}}%{{/coverage}}

Findings: total {{total}} · blocking {{blocking}}
{{#findings}}
- [{{severity}}{{#unconfirmed}}?{{/unconfirmed}}] {{type}} {{file}} {{key}} — {{detail}}
{{/findings}}

Fixes applied: {{appliedCount}} · verified: {{verified}}
Remaining risks: {{remaining}}
Status: {{status}}
Machine-readable copy: i18n audit --format json
