// playwright/tests/my_instruments.spec.ts
// Updated: 2025-08-30
// Version: 1.0
// Purpose: Smoke test for /my_instruments route.
import { test, expect } from '@playwright/test';

test('my instruments page loads', async ({ page }) => {
  await page.goto('/my_instruments');
  await expect(page.locator('h1')).toHaveText(/Instrument Catalog/);
});
