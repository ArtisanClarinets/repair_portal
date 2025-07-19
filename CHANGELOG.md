## 2025-07-18
- Split Clarinet Intake controller and desk scripts: now cleanly separated for Inventory vs Repair.
- Added `item_code` field (required for Inventory only) and updated doctype schema.
- Inventory intake now auto-creates ERPNext Serial No, Initial Intake Inspection, and Clarinet Initial Setup.
- Added `clarinet_intake_inventory.py` and `clarinet_intake_repair.py` for business logic separation.
- JS logic split into `clarinet_intake_inventory.js` and `clarinet_intake_repair.js` and loaded via hooks.py `doctype_js`.
- Robust error logging and required field enforcement on both backend and frontend.
- Added automated test for inventory intake automation.
- README.md in doctype/clarinet_intake fully explains roadmap, code, and onboarding for new devs.

## 2025-07-19
- Resolved 21 outstanding compliance errors across JSON Doctypes, Reports, Notifications, Workflows, Web Forms, Print Formats, and Dashboard files.
- Ensured all files conform to Fortune-500/Frappe v15 compliance for required keys, correct value types, and schema.
- See PR for field-by-field before/after. Validation and export-fixtures steps also performed.
- No data loss or corruption detected after patch.

**Files updated:**
- repair_logging/report/repair_tasks_by_type/repair_tasks_by_type.json (added required keys)
- service_planning/report/repair_bay_utilization/repair_bay_utilization.json (added required key)
- repair_logging/doctype/tenon_measurements/tenon_measurements.json (added permissions)
- repair_logging/doctype/tenon_fit_record/tenon_fit_record.json (added permissions)
- repair_logging/doctype/visual_inspection/visual_inspection.json (added permissions)
- repair_logging/doctype/tenon_socket_measurements/tenon_socket_measurements.json (added permissions)
- repair_logging/doctype/environment_log/environment_log.json (added permissions)
- lab/doctype/measurement_entry/measurement_entry.json (added permissions)
- instrument_profile/notification/missing_player_profile/missing_player_profile.json (added channel/send_on)
- instrument_profile/notification/missing_customer/missing_customer.json (added channel/send_on)
- customer/notification/draft_customer.json (added name/channel/send_on)
- instrument_profile/workflow/instrument_profile_workflow.json (added name)
- intake/workflow/appointment_workflow.json (added document_type)
- player_profile/workflow/player_profile_workflow.json (added workflow_name)
- intake/web_form/clarinet_intake_request/clarinet_intake_request.json (added doc_type/web_form_fields)
- repair/web_form/repair_request/repair_request.json (added title/web_form_fields)
- intake/print_format/intake_receipt.json (added print_format_type/corrected standard)
- qa/print_format/qc_certificate/qc_certificate.json (added doc_type/print_format_type)
- qa/print_format/quality_inspection/quality_inspection.json (added doc_type/print_format_type)
- customer/dashboard/customer_dashboard/customer_dashboard.json (added dashboard_name)
