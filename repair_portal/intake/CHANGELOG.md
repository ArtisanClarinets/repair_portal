# Intake Module Changelog

## [2.1.0] - 2025-10-05

### 🎯 Fortune-500 UX Hardening Follow-Through

This release completes the Fortune-500 intake desk action plan by replacing the legacy `intake_status` field with workflow-driven HTML widgets, restoring analytics, and aligning documentation, scripts, and deployment tooling with the new architecture.

### ✨ Added / Changed
- **Workflow UX:** `workflow_stage_badge` and `sla_commitment_panel` HTML fields render branded badges sourced from `workflow_state`, with cancel actions added across the workflow JSON and list view bulk actions.
- **Analytics:** `clarinet_intake_timeline.get_timeline_data` now backs the dashboard heatmap; Intake SLA Pulse report linked from workspace for executive oversight.
- **API Governance:** Controller helper duplicates removed; `repair_portal.intake.api` enforces ownership joins for serial/inspection lookups with structured logging.
- **Print Formats:** Intake Receipt modernized with QR tags, clarinet condition grids, and live field bindings using shared Jinja barcode helper.
- **Portal & Permissions:** Loaner Return Check restricted to internal roles; public intake web form expanded to capture transport photos, risk disclosures, and humidity history.
- **Fixtures & Templates:** Template loader targets intake defaults fixture (`clarinet_intake_defaults.json`) for idempotent consent/SLA seeding.
- **Verification Harness:** `verify_intake_module.py` updated to validate workflow_state-driven UX, analytics, and lint/tests with Ruff integration.
- **Docs & Tooling:** Intake README, DocType README, desk UX guide, deployment script, and changelog refreshed to reflect workflow_state architecture.

### 🛠 Fixed
- Removed stale `intake_status` references from scripts, docs, deployment scripts, and audits to prevent regressions.
- Ensured verification harness fails fast if legacy fields reappear or analytics cannot be computed.

### ✅ Verification
- `bench execute repair_portal.intake.scripts.verify_intake_module.run_verification`
- `bench run-tests --module repair_portal.intake.doctype.clarinet_intake.test_clarinet_intake`
- Intake SLA Pulse rendering validated via workspace link.

---

## [2.0.0] - 2025-10-01

### 🎉 Major Enhancements - Fortune-500 Production Readiness

Initial enterprise hardening of the intake module with consent automation, synchronization improvements, and verification coverage.

### ✨ Added

#### Consent Automation
- **Clarinet Intake Settings** gained automated consent form controls:
  - `auto_create_consent_form` (Check)
  - `default_consent_template` (Link)
  - `consent_required_for_intake_types` (Table)
- **Clarinet Intake Controller** methods `_should_create_consent()` and `_create_consent_form()` create consent forms during `after_insert()` when configured.

#### Workflow Integration
- Intake workflow transitions normalized to Frappe workflow engine with email alerts and escalation handling.
- Verification harness introduced to ensure workflow definitions remain synchronized with DocType metadata.

#### Enhanced Customer Synchronization
- `intake_sync.py` rewritten with type hints, validation, idempotent operations, and dynamic link management for Customer/Address records.

#### Comprehensive Test Suites
- **test_clarinet_intake.py:** covers item/serial/instrument creation, intake type validation, duplicate prevention, and autoname checks.
- **test_loaner_instrument.py:** status transitions, PDF generation, and business rule enforcement.
- **test_brand_mapping_rule.py:** normalization, fuzzy matching, and validation scenarios.

#### Verification Infrastructure
- **verify_intake_module.py** established to validate headers, consent automation, workflow health, test execution, and linting (baseline version).

### 🔧 Fixed
- Mandatory header format enforced across Python/JS files.
- Loaner Return Check validation hardened with internationalized error handling.
- Intake module documentation expanded for each DocType.

### 📚 Documentation
- Intake module README and DocType READMEs refreshed with consent automation and workflow overviews.

### 🔒 Security & Quality
- PEP 8 compliance, type hints, error logging with `frappe.log_error`, and secure API whitelisting maintained.

### 🔄 Migration Notes
1. Run `bench migrate` after pulling release.
2. Configure consent automation as desired in Clarinet Intake Settings.
3. Execute verification harness to confirm installation health.

---

## [1.0.0] - 2024-12-15

### Initial Release
- Core intake module functionality.
