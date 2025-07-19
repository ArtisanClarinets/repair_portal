# Instrument Profile DocType

**Location:** `repair_portal/instrument_profile/doctype/instrument_profile/`

## Overview
Instrument Profile is the central asset record for tracking clarinet instruments across their full lifecycle—inventory, intake, repair, setup, inspection, warranty, and archival. Designed for ERPNext v15 and enterprise reliability, this DocType acts as your single source of truth for asset identity, workflow state, compliance, and customer transparency.

---

## Key Features

- **Asset Master:**
  - Each Instrument Profile is a unique instrument (linked by Serial No) with instant lookups for inventory, repair, and customer service.
- **Portal-Ready Permissions:**
  - *Customers* can view only their own instrument profiles (read-only, enforced by `if_owner` rule).
  - *Repair Managers* have full lifecycle control (read, write, submit, cancel, create).
- **Warranty Sync:**
  - The `warranty_expiration` field is auto-synced from the ERPNext Serial No. Displays as a color-coded dashboard indicator (green/orange/red) for management and customer UX.
- **Integrated Workflow:**
  - Tracks the status via `workflow_state` (Open, In Progress, Delivered, Archived) with actionable buttons and real-time indicators.
- **Audit & Compliance:**
  - All major events (repairs, inspections, setups, QA, warranty, condition, materials, interactions) are logged as child tables for total traceability. No data silos.
- **ERPNext Integration:**
  - Links directly with ERPNext’s Serial No doctype for asset consistency and auto-creation (with full error capture/logging). Warns if Serial No/model mismatch.
- **Error Handling:**
  - All backend syncs are wrapped in `try/except` with error logging via `frappe.log_error()` to maintain auditability.

---

## Main Fields & Tables
- **Serial No:** Required, unique, ERPNext-linked.
- **Warranty Expiration:** Date, auto-synced, read-only, shown as dashboard indicator.
- **Workflow State:** Status managed by workflow—controls allowed actions.
- **Repair, Inspection, QA, Condition, Setup Logs:** Linked tables for full maintenance traceability.

---

## Automation & Sync Logic
- On save/update, auto-syncs warranty expiration from ERPNext Serial No.
- On update, refreshes all related logs and audits as child tables.
- If Serial No is missing in ERPNext, auto-creates it (with fallback/default model).
- Dashboard indicators provide instant visual cues for warranty, workflow, and verification state.

---

## Security & UX
- **No inline HTML:** All UI is managed via Frappe’s APIs.
- **Permission model:** Designed for both internal (Repair Manager) and portal (Customer) use, with Fortune-500 transparency and privacy.

---

## Maintenance & Extension
- Logic is fully PEP 8 and Frappe best-practice compliant.
- Add new roles or workflow states easily via the Doctype JSON and permissions arrays.
- For warranty integrations or new compliance reports, simply extend the controller and UI logic—modular by design.

---

## Change History
See `../../../../CHANGELOG.md` for all updates.
