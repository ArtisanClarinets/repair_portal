# File: repair_portal/patches/migrate_inspection_report_to_intake_inspection.py
# Last Updated: 2025-07-05
# Version: 1.0
# Purpose: Migrate all Inspection Report records to Intake Inspection, field-by-field, preserving links and data
# Dependencies: Intake Inspection must exist as a Doctype before running

import frappe

def execute():
    migrated = 0
    errors = []
    for doc in frappe.get_all("Inspection Report", fields=["name"]):
        old = frappe.get_doc("Inspection Report", doc.name)
        try:
            # Defensive: skip if already migrated (by unique constraint or same name)
            exists = frappe.db.exists("Intake Inspection", {"clarinet_intake": old.clarinet_intake, "inspection_date": old.inspection_date})
            if exists:
                continue
            new_doc = frappe.new_doc("Intake Inspection")
            # Map all common fields by fieldname
            for field in [
                "inspection_date", "instrument_id", "customer_name", "inspection_type", "procedure",
                "status", "preliminary_estimate", "clarinet_intake", "legacy_clarinet_inspection_id",
                "qc_certificate", "non_conformance_report", "digital_signature", "flag_for_reinspection"
            ]:
                if hasattr(old, field):
                    setattr(new_doc, field, getattr(old, field, None))
            # Child tables: checklist and findings
            if hasattr(old, "inspection_checklist"):
                for item in old.inspection_checklist:
                    new_doc.append("inspection_checklist", item.as_dict())
            if hasattr(old, "inspection_findings"):
                for item in old.inspection_findings:
                    new_doc.append("inspection_findings", item.as_dict())
            new_doc.insert(ignore_permissions=True)
            migrated += 1
        except Exception as e:
            errors.append(f"Failed to migrate {doc.name}: {e}")
            frappe.log_error(f"Failed to migrate Inspection Report {doc.name}: {e}", "Inspection Report Migration Error")
    frappe.msgprint(f"Migration complete. {migrated} records migrated. {len(errors)} errors.")
    if errors:
        frappe.log_error("\n".join(errors), "Inspection Report Migration Summary")
