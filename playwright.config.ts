import { defineConfig } from '@playwright/test';

export default defineConfig({
  webServer: {
    command: 'bench start',
    port: 8000,
    timeout: 120 * 1000,
  },
  testDir: './playwright/tests',
});
