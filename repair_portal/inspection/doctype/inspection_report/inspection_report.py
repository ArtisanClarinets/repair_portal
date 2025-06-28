# File: repair_portal/inspection/doctype/inspection_report/inspection_report.py
# Updated: 2025-06-27
# Version: 1.1
# Purpose: Parent Inspection document for all QA/repair/cleaning workflows. 
# On create, auto-loads checklist steps from selected procedure (Clarinet QA, etc) using JSON/Quality Procedure integration.
# Enforces pass/fail validation, NCR creation on critical failures, and requires photos for failed steps.

import frappe
from frappe.model.document import Document
from frappe import _

class InspectionReport(Document):
    def before_insert(self):
        """
        On creation: Auto-populate checklist steps from procedure if inspection_type and procedure are set.
        """
        if self.inspection_type and self.procedure and not self.inspection_checklist:
            steps = load_checklist_steps(self.procedure)
            for s in steps:
                self.append("inspection_checklist", s)

    def validate(self):
        """
        Enforce:
          - All checklist items must be completed (pass/fail)
          - Photo required for all failed steps
          - NCR auto-link/creation for any major/critical fail
        """
        for item in self.inspection_checklist:
            if not item.pass_fail:
                frappe.throw(_(f"All checklist items must have Pass/Fail set. Missing in sequence: {item.sequence} ({item.area})"))
            if item.pass_fail == "Fail" and not item.photo:
                frappe.throw(_(f"Photo is required for failed step: {item.sequence} - {item.area}"))
            if item.pass_fail == "Fail" and item.severity in ["Major", "Critical"] and not self.non_conformance_report:
                ncr = create_ncr(self, item)
                self.non_conformance_report = ncr.name
                frappe.msgprint(_(f"Non Conformance Report created: {ncr.name} for failure in {item.area}"))

    def on_submit(self):
        """
        On submit, generate QC Certificate as PDF (future step), and ensure all NCR links are present if fails occurred.
        """
        pass  # Certificate generation will be implemented separately.

def load_checklist_steps(procedure_name):
    """
    Load checklist steps from Quality Procedure (or JSON) for the given procedure_name.
    Returns list of dicts to append to child table.
    """
    # Try ERPNext Quality Procedure first
    try:
        proc = frappe.get_doc("Quality Procedure", procedure_name)
        if hasattr(proc, "processes"):
            return [
                {
                    "sequence": p.sequence,
                    "area": p.process_description,
                    "criteria": p.acceptance_criteria,
                    "severity": p.severity if hasattr(p, "severity") else "Minor"
                }
                for p in proc.processes
            ]
    except Exception:
        pass
    # Fallback: load from clarinet_qc.json via custom loader
    try:
        from repair_portal.qa.setup.clarinet_qc import load_schema
        schema = load_schema()
        for proc in schema["procedures"]:
            if proc["name"] == procedure_name:
                steps = []
                for pt in proc["points"]:
                    steps.append({
                        "sequence": pt.get("seq", 0),
                        "area": pt.get("parameter", pt.get("sub_procedure", "")),
                        "criteria": pt.get("criteria", ""),
                        "severity": "Minor"
                    })
                return steps
    except Exception as e:
        frappe.throw(_(f"Failed to load procedure checklist: {e}"))
    return []

def create_ncr(inspection, failed_item):
    """
    Create and return a Non Conformance Report linked to this inspection and failed item.
    """
    ncr = frappe.new_doc("Non Conformance Report")
    ncr.instrument_id = inspection.instrument_id
    ncr.customer_name = inspection.customer_name
    ncr.inspection_report = inspection.name
    ncr.area = failed_item.area
    ncr.severity = failed_item.severity
    ncr.notes = failed_item.notes
    ncr.insert()
    return ncr
