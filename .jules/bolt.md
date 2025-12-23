## 2025-12-18 - Add Index to Portal Token
**Learning:** Lookup fields used in public endpoints (like `portal_token`) must be indexed to prevent full table scans and denial of service.
**Action:** Added `portal_token` field to `Repair Request` with `unique: 1` to ensure database indexing.

## 2025-12-18 - Index Mail In Repair Request Link
**Learning:** `Mail In Repair Request` is queried by `repair_request` in public status pages. Missing index causes full table scans.
**Action:** Added `search_index: 1` to `repair_request` field in `Mail In Repair Request` DocType.
## 2025-12-20 - [Medium] Optimize BOM Update
**Learning:** Loops containing database updates are a common source of N+1 query problems, which can lead to significant performance degradation.
**Action:** Refactored the `_update_related_repair_orders` function in the `ClarinetBOMTemplate` controller to use a single, efficient `frappe.qb` bulk `UPDATE` query, eliminating the N+1 issue.

## 2025-12-19 - Add Core Performance Indexes
**Learning:** High-traffic dashboards and list views were missing composite indexes for common filter combinations (e.g., Customer + Status), leading to suboptimal query plans.
**Action:** Created patch `v15.add_core_indexes` to add recommended indexes for Instrument Profile, Repair Order, and Intake.

## 2025-12-21 - Optimize Intake Dashboard Counts
**Learning:** Iterative database queries (N+1) for counting statuses significantly impact performance.
**Action:** Refactored `get_intake_counts` to use a single `GROUP BY` SQL query, reducing 6 queries to 1.

## 2025-12-22 - Optimize Instrument Profile List
**Learning:** Fetching all records into memory (`get_all` without filters) and then filtering in Python is inefficient and can cause memory exhaustion (DoS).
**Action:** Updated `list_for_user` to use database-level filtering (`filters` parameter) in `get_all`, ensuring only relevant records are fetched.
