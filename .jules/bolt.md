## 2024-08-05 - N+1 Query in Client Portal

**Learning:** The `get_my_repairs` function in `repair_portal/api/client_portal.py` was making two separate database calls to fetch instrument profiles, resulting in an N+1 query problem. The first call retrieved the instrument names, and the second retrieved the instrument metadata.

**Action:** I refactored the function to combine these two calls into a single `frappe.get_all` query that retrieves all the necessary fields at once. This eliminates the redundant database call and improves the performance of the API endpoint.
## 2025-12-19 - Add Core Performance Indexes
**Learning:** High-traffic dashboards and list views were missing composite indexes for common filter combinations (e.g., Customer + Status), leading to suboptimal query plans.
**Action:** Created patch `v15.add_core_indexes` to add recommended indexes for Instrument Profile, Repair Order, and Intake.

## 2025-12-21 - Optimize Intake Dashboard Counts
**Learning:** Iterative database queries (N+1) for counting statuses significantly impact performance.
**Action:** Refactored `get_intake_counts` to use a single `GROUP BY` SQL query, reducing 6 queries to 1.

## 2025-12-22 - Optimize Instrument Profile List
**Learning:** Fetching all records into memory (`get_all` without filters) and then filtering in Python is inefficient and can cause memory exhaustion (DoS).
**Action:** Updated `list_for_user` to use database-level filtering (`filters` parameter) in `get_all`, ensuring only relevant records are fetched.

## 2025-12-22 - Prevent Unbounded Fetches
**Learning:** Fetching all records without a limit can cause Out Of Memory (OOM) errors as data grows.
**Action:** Added a safe limit of 500 to `list_for_user` in `repair_portal/api/frontend/instrument_profile.py` for staff users.
