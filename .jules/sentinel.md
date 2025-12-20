## 2025-12-18 - [Critical] Prevent Unauthorized Instrument Takeover
**Vulnerability:** The public mail-in repair form allowed any user to transfer ownership of an existing instrument to themselves by submitting a request with a matching serial number.
**Learning:** Public-facing forms with `ignore_permissions=True` must never perform sensitive updates based on unverified user input.
**Prevention:** Removed logic that automatically updated `Instrument.customer` on serial number collision. Mismatches are now preserved for staff review.

## 2025-12-18 - Ensure Address Linking for Data Integrity
**Vulnerability:** Reusing existing addresses without ensuring they are linked to the current customer creates "orphan" usage.
**Learning:** Shared entity usage must enforce explicit linking to the current owner.
**Prevention:** Updated `_ensure_address` to explicitly link found addresses to the current customer.

## 2025-12-19 - Safe Query Construction with Query Builder
**Vulnerability:** Raw SQL queries using f-strings for WHERE clauses (even with parameters) can be flagged as potential injection vectors and are harder to maintain.
**Learning:** Frappe's `frappe.qb` provides a safer, more readable abstraction for constructing complex queries with dynamic filters.
**Prevention:** Refactored `get_optimized_instrument_list` to use `frappe.qb`, eliminating raw SQL string interpolation.
