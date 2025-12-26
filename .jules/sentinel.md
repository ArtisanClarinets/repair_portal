## 2024-08-05 - Security Scan and Manual Review

**Vulnerability:** None Found

**Learning:** The initial `bandit` scan produced a significant number of false positives, with incorrect file paths that made it impossible to locate the reported issues. A manual review of the `repair_portal/api` directory did not reveal any obvious SQL injection vulnerabilities or other critical security flaws. The code appears to be using the Frappe ORM correctly, which mitigates many common SQL injection risks.

**Prevention:** In the future, it would be beneficial to have a more accurate and up-to-date security scanning tool, or to have a baseline of known false positives to ignore. It would also be helpful to have a better understanding of the project structure before diving into the code.
## 2025-12-19 - Safe Query Construction with Query Builder
**Vulnerability:** Raw SQL queries using f-strings for WHERE clauses (even with parameters) can be flagged as potential injection vectors and are harder to maintain.
**Learning:** Frappe's `frappe.qb` provides a safer, more readable abstraction for constructing complex queries with dynamic filters.
**Prevention:** Refactored `get_optimized_instrument_list` to use `frappe.qb`, eliminating raw SQL string interpolation.

## 2025-10-16 - [High] IDOR in Technician Dashboard
**Vulnerability:** `get_dashboard_data` endpoint allowed any logged-in user to fetch dashboard metrics for any technician by ID.
**Learning:** API endpoints accepting a user ID parameter must validate that the requester is either that user or has privileged management roles.
**Prevention:** Added explicit check comparing `technician` argument to `frappe.session.user` and requiring 'Repair Manager' or 'System Manager' role for mismatches.

## 2025-12-21 - [High] Secure Intake Dashboard
**Vulnerability:** The `get_intake_counts` endpoint exposed global intake statistics to all logged-in users without permission checks.
**Learning:** `@frappe.whitelist(allow_guest=False)` does not imply data access permissions; explicit `frappe.has_permission` checks are required.
**Prevention:** Added `frappe.has_permission("Clarinet Intake", "read")` check to `repair_portal/api/intake_dashboard.py`.

## 2025-12-22 - [Medium] Rate Limit DoS Vulnerability
**Vulnerability:** The `rate_limited` decorator in `repair_portal/core/security.py` grouped all Guest users under a single "Guest" key, allowing one malicious IP to exhaust the rate limit for all public users.
**Learning:** Rate limiting for unauthenticated users (Guests) must use IP address or another unique identifier, not the shared session user ID.
**Prevention:** Updated `rate_limited` to use `frappe.local.request_ip` as the key when the user is "Guest".

## 2025-12-22 - [High] Secure Intake Dashboard List
**Vulnerability:** The `get_recent_intakes` endpoint used `frappe.get_all` which bypasses User Permissions (row-level security), potentially exposing all intakes to users with global read access.
**Learning:** `frappe.get_all` ignores User Permissions; `frappe.get_list` must be used when row-level security is required.
**Prevention:** Replaced `frappe.get_all` with `frappe.get_list` in `repair_portal/api/intake_dashboard.py`.
