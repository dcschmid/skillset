# Design Authenticity Audit — harbor-ferry-dashboard — 2026-11-14 (example)

## 1 Project overview
Astro 7.4 + CSS Modules, tokens src/styles/tokens.css, 14 routes, dev `npm run
dev`, Playwright present (a11y skill tooling), CI present (github).

## 2 Scope  routes /, /schedules, /admin/users · mobile+desktop · light+dark
## 3 Tools  Playwright screenshots (audit dir), build+test commands, a11y tool
## 4 Checked  12 render states + keyboard walk · NOT TESTED: auth flow (no seeded creds)

## 5 Findings  0 blocker · 3 major · 5 minor · 4 nit

## 6 Score (heuristic, evidence: renders at reports/shots/)
| axis | before | after fixes |
identity 16/20→19 · typography 12/15→14 · layout 11/15→13 · fit 13/15→14 ·
components 7/10→9 · content 9/10→9 · responsive 4/5→5 · a11y 8/10→10 => 80→93

## 7 By severity (schema: anti-ai-patterns.md)
major C1 schedules hero+3-cards template · major J1 3 button radii · major A1
default indigo accent vs marine brand · minor ×5 spacing/type drift …
## 8 Recommendations  token-level fixes first; page-level only where content differs
## 9 Applied (audit_and_fix)  tokens.css (A1), Button.variants (J1),
schedules/+page.astro (C1) — planned-not-applied: pricing grid (kept, parallel plans)
## 10 Before/after  pairs reports/shots/{before,after}/schedules-1440x900-light.png
## 11 Tests  build ok, tests 48/48, a11y tool 0 AA violations (was 2)
## 12 Open  auth-flow untested; nit list deferred
## 13 Limitations  admin dark-mode states sampled, not exhaustive; scores heuristic
