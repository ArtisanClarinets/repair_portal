# Final QA Checklist DocType

**Location:** `repair_portal/qa/doctype/final_qa_checklist/`

## Overview
Final QA Checklist enforces world-class quality control and compliance for every instrument or repair completion. Designed for technician, service manager, and customer transparency. Now includes error logging and automated workflow state syncing.

---

## Key Features
- **Validation:** Cannot submit unless all checklist items are checked.
- **Status Automation:** Updates linked Instrument Profile to "QA Complete" on submit. Also syncs workflow_state if field exists.
- **Audit Logging:** All submit logic wrapped in try/except with `frappe.log_error()` for compliance and traceability.
- **Permissions:**
  - QA Technician: Read, Write, Submit
  - Service Manager/System Manager: Full
  - Customer: Read-only (for QA transparency)
- **Reports & Analytics:**
  - All QA events are tracked for dashboard and compliance reporting.
- **Portal Ready:** Safe for customer/portal read; no PII or sensitive data exposed.

---

## Extension & Maintenance
- Add new checklist templates or workflow states as business logic evolves.
- All logic is PEP 8, v15, and audit-compliant.
- For new fields or reporting needs, extend via JSON and controller.

---

## Change Log
- 2025-07-17: Error logging, workflow_state automation, and Customer permission added.
- See `/CHANGELOG.md` for project-wide history.
