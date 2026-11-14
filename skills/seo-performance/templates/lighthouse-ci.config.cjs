// lighthouserc.cjs — Lighthouse CI (v0.16.x, verified 2026-11-14).
// Budgets are project-tunable: edit numbers to measured reality, never to ideals.
// Lab metrics gate here; INP (field metric) is NOT gated — see performance-budgets.json.
module.exports = {
  ci: {
    collect: {
      numberOfRuns: 2,                     // tolerance against lab noise
      startServerCommand: 'npm run build && npx serve dist',
      startServerReadyPattern: 'Serving|localhost',
      url: ['http://localhost:3000/', 'http://localhost:3000/about/'],
      settings: { chromeFlags: '--headless --no-sandbox --disable-dev-shm-usage' },
    },
    assert: {
      rules: {
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['warn', { maxNumericValue: 300 }],
        'server-response-time': ['warn', { maxNumericValue: 800 }],
        'resource-summary:script:size': ['error', { maxNumericValue: 170 * 1024 }],
        'resource-summary:total:size': ['error', { maxNumericValue: 800 * 1024 }],
        'categories:performance': ['warn', { minScore: 0.8 }],
      },
    },
    upload: { target: 'temporary-public-storage' },
  },
};
