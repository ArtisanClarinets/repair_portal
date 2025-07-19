# CHANGELOG – Customer Module

All changes are compliant with Frappe v15 and Fortune-500 grade engineering standards.

---

## [v1.2.1] – 2025-07-17
### 🛠️ Compliance & Workflow Fixes
- **Added missing `profile_status` field to `customer.json`** for workflow compatibility with `Customer Workflow` (states: Draft, Active, Approved, Archived, Deleted).
- Confirmed all state options in Select field match workflow.
- Audit verified: no deprecated fields, robust permissions, and all subdoctypes compliant.
- Next action: expand test coverage for workflow transitions in `test_customer.py`.

---

## [v1.2.0] – 2025-07-16
### ✨ Enhancements
- Centralized `handle_workflow_action()` logic with robust workflow-state transition handling.
- Dynamic dashboard card linking added to `customer_dashboard.json`.
- Enforced `entry_date` and `method` validation in `ConsentLogEntry`.
- Enforced `date_given` and `consent_type` validation in `ConsentLog`.
- Added graceful failure handling to `client_portal.js` via `.catch()` for `frappe.require()`.

### 🔁 Workflow Fixes
- `Restore` now correctly transitions from `Archived` ➝ `Active`.
- `Delete` now limited to `Active` ➝ `Deleted` only.

### ✅ Tests
- Refactored `test_customer.py` to use dynamic record loading.

### 📦 Refactors
- Standardized file headers for all Python controllers.
- Improved docstring and method documentation consistency.

---

## [v1.1.0] – 2025-06-30
- Initial modularization of workflow logic and profile syncing.
- Added notifications and user-based auto-profile creation.
