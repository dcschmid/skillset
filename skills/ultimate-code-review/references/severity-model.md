# Severity & confidence model

Severity answers "how bad if real"; confidence answers "how sure are we".
Both travel on every finding; gates read both.

| severity | meaning | gate effect (level=all) |
|---|---|---|
| critical | broken build/data loss/exploit | blocks when open+verified |
| high | wrong behavior users hit | blocks at `high`+ |
| medium | quality/maintainability drag | warning |
| low | small defect/polish | warning |
| info | note, no action | never blocks |

| confidence | bar | gate-blockable |
|---|---|---|
| confirmed | ran/compiled/reproduced | yes |
| strong-evidence | mechanism visible in code | yes |
| suspected | pattern-level, unproven | no (warning) |
| needs-verification | needs runtime/env to tell | no (warning) |

Skipped checks (SPEC_NOT_AVAILABLE, absent tool, axis agent died) are a
third category: neither finding nor pass — they land in `skipped_axes` and
Limitations. A gate PASS requires no blocking findings AND no invalid
findings; it does NOT require zero skips, but skips stay visible so a human
can decide whether the remaining coverage is enough.

Calibration: severity from impact, never from axis enthusiasm. Two agents
reporting one defect → one finding, both axes linked via `also_flagged_by`;
counts don't double.
