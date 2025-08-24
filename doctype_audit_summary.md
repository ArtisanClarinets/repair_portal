# repair_portal — Doctype Audit Summary

Purpose
- Central README that consolidates the DocTypes discovered by the repository audit.
- Use this file as a quick registry and pointer to the detailed, machine-readable audit at `.doctype_audit_report.json`.

Where to find the full audit
- File: repair_portal/.doctype_audit_report.json
- Contains per-file paths, discovered field metadata and an issues list produced by the static auditor.

How to use this README
- Use the DocType list below to quickly navigate to each DocType directory.
- Use the audit JSON for exact file paths and field counts (recommended when editing schema or controllers).
- When changing any `.py` or `.js` file, follow the mandatory header rules in COPILOT_INSTRUCTIONS.md §5 and run the verification checklist.

DocTypes discovered by the audit
(Every DocType listed in .doctype_audit_report.json)

- Consent Field Value
- Consent Form
- Consent Log
- Consent Log Entry
- Consent Required Field
- Consent Template
- Customer Consent
- Customer Type
- Instruments Owned
- Linked Players
- Customer Upgrade Request
- Upgrade Option
- Instrument Inspection
- Client Instrument Profile
- Customer External Work Log
- Instrument
- Instrument Accessory
- Instrument Category
- Instrument Condition Record
- Instrument Model
- Instrument Photo
- Instrument Profile
- Instrument Serial Number
- Clarinet Initial Setup
- Clarinet Pad Entry
- Clarinet Pad Map
- Clarinet Setup Log
- Clarinet Setup Operation
- Clarinet Setup Task
- Clarinet Task Depends On
- Clarinet Template Task
- Clarinet Template Task Depends On
- Setup Checklist Item
- Setup Material Log
- Setup Template
- Brand Mapping Rule
- Clarinet Intake
- Clarinet Intake Settings
- Intake Accessory Item
- Loaner Instrument
- Loaner Return Check
- Pad Count Intake
- Pad Count Log
- Environment Log
- Measurement Entry
- Measurement Session
- Player Equipment Preference
- Player Profile
- Final Qa Checklist
- Final Qa Checklist Item
- Default Operations
- Operation Template
- Pulse Update
- Repair Feedback
- Repair Issue
- Repair Order
- Repair Request
- Repair Task
- Barcode Scan Entry
- Diagnostic Metrics
- Instrument Interaction Log
- Key Measurement
- Material Use Log
- Pad Condition
- Related Instrument Interaction
- Repair Parts Used
- Repair Task Log
- Tenon Measurement
- Tone Hole Inspection Record
- Tool Usage Log
- Visual Inspection
- Warranty Modification Log
- Qa Checklist Item
- Technician
- Repair Portal Settings
- Estimate Line Item
- Repair Estimate
- Service Plan
- Service Task
- Tasks
- Tool
- Tool Calibration Log

Notes & flagged issues (from the audit)
- The audit includes an issues array. Example findings:
  - intra_doctype_duplicate_label_case_insensitive for "Repair Request": duplicate labels (status, repair notes, qa checklist) — please inspect the DocType JSON and remove/merge duplicate labels or rename fields to be unique.
- For each DocType, open `.doctype_audit_report.json` to see:
  - file paths (primary JSON files),
  - field counts,
  - per-field metadata and any warnings/errors.

Recommended next steps for maintainers
- Before editing any DocType JSON or controller:
  - Back-trace Link/Table targets to ensure they exist (COPILOT §9).
  - Add/verify `README.md` next to any DocType changed (COPILOT §8.1).
  - Add/update mandatory file headers in changed `.py` and `.js` files (COPILOT §5).
  - Run linting and the audit script (scripts/validate_doctypes.py) and fix any errors/warnings.
  - Add tests for any business-rule changes (COPILOT §10).

Verification Checklist (local)
# Pull latest & migrate
bench --site erp.artisanclarinets.com migrate

# Build assets
bench build

# Run targeted tests (replace <module>)
bench --site erp.artisanclarinets.com run-tests --module repair_portal.tests.<module>

# Run the doctype auditor
python3 repair_portal/.doctype_audit_report.json  # (or open the JSON directly); run scripts/validate_doctypes.py for validation

# Optional: run full suite
bench --site erp.artisanclarinets.com run-tests --app repair_portal

Changelog
- 2025-08-22 — 1.0.0 — Initial consolidated README generated from .doctype_audit_report.json.
