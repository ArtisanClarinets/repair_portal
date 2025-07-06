# File Header Template
# Relative Path: repair_portal/inspection/doctype/intake_inspection/intake_inspection.py
# Last Updated: 2025-07-06
# Version: v1.3
# Purpose: Intake Inspection document for clarinet QA, repair, and cleaning.
# Enforces checklist validation, NCR creation, reinspection notifications, and delivery-triggered acclimatization scheduling.
# Dependencies: frappe.email, frappe.utils, Quality Procedure

import frappe
from frappe import _
from frappe.model.document import Document

class IntakeInspection(Document):
    def before_insert(self):
        """Auto-populate checklist steps from Quality Procedure or fallback JSON schema."""
        if self.inspection_type and self.procedure and not self.inspection_checklist:
            steps = load_checklist_steps(self.procedure)
            for s in steps:
                self.append("inspection_checklist", s)

    def validate(self):
        """Validate completeness and enforce business rules."""
        for item in self.inspection_checklist:
            if not item.pass_fail:
                frappe.throw(
                    _(f"Checklist item missing Pass/Fail: {item.sequence} ({item.area})")
                )
            if item.pass_fail == "Fail" and not item.photo:
                frappe.throw(
                    _(f"Photo required for failed step: {item.sequence} - {item.area}")
                )
            if (
                item.pass_fail == "Fail"
                and item.severity in ["Major", "Critical"]
                and not self.non_conformance_report
            ):
                try:
                    ncr = create_ncr(self, item)
                    self.non_conformance_report = ncr.name
                    frappe.msgprint(
                        _(f"Non Conformance Report created: {ncr.name}")
                    )
                except Exception:
                    frappe.log_error(frappe.get_traceback(), "NCR Creation Failed")
        if self.flag_for_reinspection:
            notify_reinspection(self)

    def on_submit(self):
        """Enforce final signature and schedule acclimatization if delivered."""
        if not self.digital_signature:
            frappe.throw(_("Digital signature required for submission."))
        if getattr(self, "instrument_delivered", 0):
            try:
                schedule_acclimatization_reminder(self)
            except Exception:
                frappe.log_error(frappe.get_traceback(), "Acclimatization Reminder Failed")

def load_checklist_steps(procedure_name):
    """Load checklist steps from ERPNext Quality Procedure or fallback JSON."""
    try:
        proc = frappe.get_doc("Quality Procedure", procedure_name)
        return [
            {
                "sequence": p.sequence,
                "area": p.process_description,
                "criteria": p.acceptance_criteria,
                "severity": getattr(p, "severity", "Minor"),
            }
            for p in proc.processes
        ]
    except Exception:
        pass
    try:
        from repair_portal.qa.setup.clarinet_qc import load_schema
        schema = load_schema()
        for proc in schema["procedures"]:
            if proc["name"] == procedure_name:
                return [
                    {
                        "sequence": pt.get("seq", 0),
                        "area": pt.get("parameter", pt.get("sub_procedure", "")),
                        "criteria": pt.get("criteria", ""),
                        "severity": "Minor",
                    }
                    for pt in proc["points"]
                ]
    except Exception as e:
        frappe.throw(_(f"Checklist load failed: {e}"))
    return []

def create_ncr(inspection, failed_item):
    """Create a Non Conformance Report linked to this inspection."""
    ncr = frappe.new_doc("Non Conformance Report")
    ncr.instrument_id = inspection.instrument_id
    ncr.customer_name = inspection.customer_name
    ncr.intake_inspection = inspection.name
    ncr.area = failed_item.area
    ncr.severity = failed_item.severity
    ncr.notes = failed_item.notes
    ncr.insert()
    return ncr

def notify_reinspection(inspection):
    """Notify QA team about reinspection."""
    try:
        qa_users = frappe.get_all(
            "User",
            filters={"roles.role": ["in", ["QA Manager", "Technician"]]},
            fields=["email"]
        )
        recipients = [u.email for u in qa_users if u.email]
        if recipients:
            frappe.sendmail(
                recipients=recipients,
                subject="Intake Inspection flagged for reinspection",
                message=f"Inspection {inspection.name} flagged for reinspection."
            )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Reinspection Notification Failed")

def schedule_acclimatization_reminder(doc):
    """Schedule 6-month bore oiling and service reminder after delivery."""
    reminder_date = frappe.utils.add_months(doc.modified, 6)
    frappe.get_doc({
        "doctype": "ToDo",
        "owner": doc.owner,
        "reference_type": doc.doctype,
        "reference_name": doc.name,
        "date": reminder_date,
        "description": _("6-month bore oiling reminder for instrument {0}").format(doc.instrument_id or ""),
        "status": "Open"
    }).insert(ignore_permissions=True)
