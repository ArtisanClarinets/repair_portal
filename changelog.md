# Changelog

## 2025-08-30
- **package.json** ➜ added Vite + Playwright dependencies and scripts.
- **vite.config.ts** ➜ new Vite build config with SSR target classic.
- **apps.json** ➜ registered build for bench.
- **README.md** ➜ documented npm dev and bench build commands.
- **public/js/wellness_dashboard.js** ➜ removed; logic moved to composable.
- **vue/composables/useWellness.ts** ➜ new TypeScript composable.
- **vue/pages/InstrumentWellness.vue** ➜ new page component.
- **vue/pages/MyInstruments.vue** ➜ new page component with fallback logic.
- **api/instrument.py** ➜ added whitelisted REST helpers.
- **playwright/tests/my_instruments.spec.ts** ➜ smoke test.
- **playwright.config.ts** ➜ Playwright config.
- **patches/** ➜ diff snippets illustrating refactors.
