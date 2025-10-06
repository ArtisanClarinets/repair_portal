# Intake Module

**Location:** `repair_portal/intake/`
**Last Updated:** 2025-10-05
**Version:** 2.1.0

## Overview
The Intake module orchestrates the full lifecycle of instrument and accessory intake, service initiation, and tracking for clarinet and related assets. It is the first touchpoint for inventory, customer drop-offs, and repair workflows, ensuring every asset and action is logged, validated, and fully traceable.

**Recent Enhancements (v2.1.0):**
- ✅ All files updated with mandatory 5-line headers (Path/Date/Version/Description/Dependencies)
- ✅ Workflow UI refactored to rely on `workflow_state` with HTML badges and SLA panels (legacy `intake_status` removed)
- ✅ Consent automation implemented (auto-creates consent forms based on settings)
- ✅ Enhanced `intake_sync.py` with type hints, validation, and idempotent operations
- ✅ Intake SLA Pulse dashboard/report delivered for executive monitoring
- ✅ Consolidated intake APIs with ownership enforcement and structured logging

---

## Main Components

- **Doctypes:**
  - **Clarinet Intake:** The master record for every intake (inventory, customer, repair). Handles workflow, ownership, linkage to setups, and downstream automation. **NEW:** Workflow badges and SLA panels rendered from `workflow_state` alongside consolidated API calls.
  - **Loaner Instrument:** Manages assignment, agreement PDF, and lifecycle of loaner assets. Auto-generates agreements and logs errors reliably. **Enhanced with internal-only QA permissions.**
  - **Brand Mapping Rule:** Normalizes brand names with fuzzy matching for consistent data entry. **Enhanced with validation and test coverage.**
  - **Accessory Items, Checklists, Return Checks:** Structured doctypes for asset/accessory traceability and compliance.

- **Workflow:**
  - **Workflow JSON:** `intake/workflow/intake_workflow/intake_workflow.json` drives all transitions using `workflow_state` with cancel actions for every stage.
  - **Transitions:** Automated and manual, enforced via Frappe workflow engine. Supports portal and internal review.
  - **Tests:** Workflow state tests validated via the verification harness.

- **Automation & Controllers:**
  - **Python controllers** for all core doctypes.
  - Automated linking of setups, logs, service/repair, and QA events to intakes and instrument profiles.
  - Loaner agreement generation robustly error-handled (`frappe.log_error`).

- **Reports & Dashboards:**
  - **Operational Reports:** Loaners outstanding, loaner turnover, intake by day, follow-up compliance, deposit balance aging, loaner return flags. All in `/report/` folders with JSON+Python.
  - **Dashboard Charts:** Intake SLA Pulse, appointments by week, overdue intakes, intakes due soon, average intake-to-repair, loaners checked out—JSON-based, ready for dashboard plug-and-play.

- **Print Formats:**
  - Intake receipt and desk labels under `/print_format/` include QR codes, condition grids, and technician sign-offs.

- **Web Forms:**
  - Portal-ready intake request web form capturing transport details, risk disclosures, humidity history, and photo bundles.

- **Config & Utilities:**
  - Desktop icon configs, workflow definition helpers, and email utilities for notifications (e.g., `/utils/emailer.py`).

- **Testing:**
  - `/test/` folder contains full-flow intake tests and verification harness coverage.

- **Automation Scripts & Hooks:**
  - **Hooks:** Event hooks for workflow reloading, compliance automation, and error logging. Scripts follow best practices for Frappe v15 and auditability.
  - **Template Loader:** `hooks/load_templates.py` installs intake defaults (consent, SLA) from curated fixtures.

- **Compliance & Quality:**
  - PEP 8, Fortune-500 polish, robust docstrings and inline comments.
  - Every major action wrapped in try/except with `frappe.log_error` for bulletproof auditing.
  - Change history maintained at the project root (`CHANGELOG.md`).

---

## How Everything Connects

- **Inventory Intake:**
  - Triggers creation and linking of initial setup, logs, and instrument profile.
  - Workflow badges show SLA commitments and overdue alerts at a glance.

- **Loaner Issuance:**
  - Customer/asset linked, agreement PDF generated, document attached.
  - On failure, errors are logged and surfaced with actionable messages.

- **Customer Portal:**
  - Role-based permissioning: customers only see their intakes; internal users manage the full lifecycle.

- **Reporting & Dashboarding:**
  - Intake SLA Pulse, loaner backlog, and compliance activity visible in operational dashboards and reports—enterprise ready.

---

## Extension & Maintenance

- Add new workflow states, doctypes, or automation scripts as your processes grow—update `workflow_state` values and client badges simultaneously.
- Extend verification harness tests when introducing new APIs or desk widgets.
- Use migration and fix scripts to keep all metadata 100% v15 compatible and audit-safe.

---

## For More Info
- See `/repair_portal/CHANGELOG.md` for full historical updates.
- Each doctype and script contains its own header for traceability.
- Run `bench execute repair_portal.intake.scripts.verify_intake_module.run_verification` to confirm environment health.

---

**This module is architected for transparency, compliance, and enterprise scale—no technical debt, no silos, and robust error logging at every step.**
