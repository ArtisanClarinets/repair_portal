## 2025-12-18 - Add Index to Portal Token
**Learning:** Lookup fields used in public endpoints (like `portal_token`) must be indexed to prevent full table scans and denial of service.
**Action:** Added `portal_token` field to `Repair Request` with `unique: 1` to ensure database indexing.
