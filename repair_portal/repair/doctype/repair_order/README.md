# Repair Order DocType

**Location:** `repair_portal/repair/doctype/repair_order/`

## Overview
Repair Order manages the lifecycle for all repairs—intake, processing, billing, QA, and analytics. Fully integrated with ERPNext v15, supporting technician, customer, and executive UX. All automation is Fortune-500 compliant, now with audit-grade error logging.

---

## Key Features
- **Validation:** Customer and issue description are required.
- **Warranty Logic:** Auto-detects warranty repairs based on linked Instrument Profile. Sets is_warranty and comments accordingly.
- **Error Logging:** All backend automation is in try/except with `frappe.log_error()` for maximum traceability and support.
- **Workflow Automation:** Hooks in place for time logging, labor automation, and status change (extendable per business needs).
- **Permissions:**
  - Technician/System Manager: Full access
  - Customer: Read-only (for portal transparency)
- **Analytics & Dashboards:**
  - Status, turnaround, technician KPIs, and cost reports are present for management.
  - Robust integration with operational and financial dashboards.
- **Portal Ready:**
  - Customers can see their repair orders and statuses via the portal or web form.

---

## Extension & Maintenance
- Extend automation in on_submit for labor logs or workflow transitions as needed.
- Add new reports or dashboard metrics via Frappe’s reporting engine.

---

## Change Log
- 2025-07-17: Error logging and Customer read permission added. Documentation updated for v15 and Fortune-500 readiness.
- See `/CHANGELOG.md` for global project log.
