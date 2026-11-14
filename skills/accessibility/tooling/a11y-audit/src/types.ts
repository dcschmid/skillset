// Shared types (erasable-syntax-only; runs on node --experimental-strip-types).

export type Level = 'a' | 'aa' | 'aaa';

export type StepResult = 'PASS' | 'FAIL' | 'NEEDS MANUAL REVIEW' | 'NOT APPLICABLE' | 'NOT TESTED';

export interface StepDef {
  // one interaction step inside a scenario
  click?: string;          // CSS selector to click
  fill?: [string, string]; // [selector, text]
  press?: string;          // keyboard key, e.g. 'Escape', 'Tab', 'Enter'
  hover?: string;
  waitFor?: string;        // wait for selector visibility
  waitMs?: number;
  expect?: string;         // selector expected visible after step (finding if not)
}

export interface RouteDef {
  name: string;
  url: string;
  auth?: boolean;          // run config.auth steps first on this page
  scenarios?: { name: string; steps: StepDef[] }[];
}

export interface Config {
  baseUrl?: string;
  routes: RouteDef[];
  auth?: { name?: string; steps: StepDef[] }; // login fixture; no secrets inline — use env placeholders ${A11Y_USER}/${A11Y_PASS}
  level?: Level;
  browser?: 'chromium' | 'firefox';
  viewports?: ('desktop' | 'mobile')[];
  out?: string;
  formats?: string[];
  rules?: Record<string, { enabled: boolean }>; // extra rule enable/disable
  timeoutMs?: number;
}

export interface Finding {
  ruleId: string;
  sc: string;               // WCAG SC id, e.g. "1.4.3" or "label"
  scName: string;
  level: 'A' | 'AA' | 'AAA' | 'BP';
  impact: string;
  route: string;
  viewport: string;
  scenario: string;
  message: string;
  selector: string;
  html: string;             // truncated outerHTML
  fix?: string;             // concrete remediation hint
  repro: string[];          // numbered reproduction steps
  manualVerification: boolean;
}

export interface ManualItem {
  sc: string;
  scName: string;
  level: string;
  reason?: string;
  how: string;
  status: 'NEEDS MANUAL REVIEW' | 'NOT TESTED';
}

export interface RouteResult {
  route: string;
  url: string;
  viewport: string;
  scenario: string;
  pass: number;
  incomplete: Finding[];    // axe "needs review" → manual review, never PASS
  violations: Finding[];
  inapplicableCount: number;
  notes: string[];
}

export interface AuditResult {
  tool: string;
  toolVersion: string;
  axeVersion: string;
  generatedAt: string;
  standard: string;
  level: Level;
  browser: string;
  os: string;
  summary: {
    routes: number;
    scenariosRun: number;
    violationsAa: number;   // blocking: level <= target, normative
    violationsAaa: number;  // advisory unless --strict-aaa
    needsManualReview: number;
    passes: number;
  };
  findings: Finding[];
  manual: ManualItem[];
  routes: RouteResult[];
  gate: 'PASS' | 'FAIL';
  gateNote: string;
}
