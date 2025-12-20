## 2025-12-18 - [Critical] Prevent Unauthorized Instrument Takeover
**Vulnerability:** The public mail-in repair form allowed any user to transfer ownership of an existing instrument to themselves by submitting a request with a matching serial number.
**Learning:** Public-facing forms with `ignore_permissions=True` must never perform sensitive updates based on unverified user input.
**Prevention:** Removed logic that automatically updated `Instrument.customer` on serial number collision. Mismatches are now preserved for staff review.

## 2025-12-18 - Ensure Address Linking for Data Integrity
**Vulnerability:** Reusing existing addresses without ensuring they are linked to the current customer creates "orphan" usage.
**Learning:** Shared entity usage must enforce explicit linking to the current owner.
**Prevention:** Updated `_ensure_address` to explicitly link found addresses to the current customer.

## 2025-05-21 - [High] Missing Role Checks in Lab API
**Vulnerability:** Publicly whitelisted functions `save_tone_fitness` and `save_leak_test` allowed any logged-in user to create records using `ignore_permissions=True` without validating the user's role.
**Learning:** `ignore_permissions=True` bypasses framework permission checks; explicit role validation is mandatory for privileged actions exposed via API.
**Prevention:** Added checks for 'Technician' or 'Lab' roles to match existing API patterns.
