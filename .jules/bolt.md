## 2025-12-18 - Add Index to Portal Token
**Learning:** Lookup fields used in public endpoints (like `portal_token`) must be indexed to prevent full table scans and denial of service.
**Action:** Added `portal_token` field to `Repair Request` with `unique: 1` to ensure database indexing.

## 2025-12-18 - Index Mail In Repair Request Link
**Learning:** `Mail In Repair Request` is queried by `repair_request` in public status pages. Missing index causes full table scans.
**Action:** Added `search_index: 1` to `repair_request` field in `Mail In Repair Request` DocType.

## 2025-12-19 - Add Core Performance Indexes
**Learning:** High-traffic dashboards and list views were missing composite indexes for common filter combinations (e.g., Customer + Status), leading to suboptimal query plans.
**Action:** Created patch `v15.add_core_indexes` to add recommended indexes for Instrument Profile, Repair Order, and Intake.
