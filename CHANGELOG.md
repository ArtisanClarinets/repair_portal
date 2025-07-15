### v2.0.0 - Major Doctype Consolidation & API Refactor (2025-07-14)

- 🚀 **Merged `Repair Request` into `Repair Order`** for total system clarity, zero duplication, and future-proof upgrades:
  - All fields, tables, statuses, and logic from `Repair Request` are now part of `Repair Order`.
  - Permissions: Only `Repair Order` is now used for all repair tracking (Tech + System Manager full perms).
  - API and dashboard endpoints refactored: ALL references to `Repair Request` are gone—dashboards, KPIs, and portals now use only `Repair Order`.
  - Reports updated: All issue and revenue/cost reports pull from `Repair Order`.
  - Controller unified: Validations, warranty logic, and submit events merged and modernized.
  - Data migration patch added: `/patches/v15_merge_repair_request_to_repair_order.py` for safe, idempotent migration (no records deleted automatically).
- 🔥 **How to deploy:**
  1. Backup your site & DB (SOC-2 best practice).
  2. Run: `bench --site erp.artisanclarinets.com migrate`
  3. Run: `bench build`
  4. Review migrated data and dashboards for accuracy.
  5. Retire `Repair Request` doctype and files *only after* UAT signoff and backup.

---

### v1.5.1 - Serial Number Integration

- 🔗 `Instrument Profile` now integrates with ERPNext's `Serial No`:
  - New Link field: `erpnext_serial_no` (hidden, staff-only)
  - Auto-creates missing `Serial No` records based on `serial_number`
  - Validates model alignment
  - All sync actions log exceptions with `frappe.log_error()`

