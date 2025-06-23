// playwright/tests/customer_sign_off.spec.ts
// Updated: 2025-09-01
// Version: 1.0
// Purpose: Smoke test for Customer Sign-Off page.
import { test, expect } from '@playwright/test';

test('customer sign-off page loads', async ({ page }) => {
  await page.goto('/customer_sign_off?repair=TEST');
  await expect(page.locator('h1')).toHaveText(/Customer Sign-Off/);
});
