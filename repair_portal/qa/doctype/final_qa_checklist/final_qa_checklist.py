# ---------------------------------------------------------------------------
# File: repair_portal/qa/doctype/final_qa_checklist/final_qa_checklist.py
# Date Updated: 2025-07-17
# Version: v1.3
# Purpose: Validates QA checklist completion, updates Instrument Profile status, and logs errors on submit.
# ---------------------------------------------------------------------------

import frappe
from frappe import _
from frappe.model.document import Document


class FinalQaChecklist(Document):
    def validate(self):
        incomplete = [i.description for i in self.items if not i.is_checked]
        if incomplete:
            frappe.throw(
                _("Cannot submit. The following items are incomplete:\n{0}").format("\n".join(incomplete))
            )

    def on_submit(self):
        try:
            if self.instrument_profile:
                frappe.db.set_value("Instrument Profile", self.instrument_profile, "status", "QA Complete")
                # Optional: update workflow_state if field exists
                if frappe.db.has_column("Instrument Profile", "workflow_state"):
                    frappe.db.set_value(
                        "Instrument Profile",
                        self.instrument_profile,
                        "workflow_state",
                        "QA Complete",
                    )
        except Exception:
            frappe.log_error(frappe.get_traceback(), "FinalQaChecklist: on_submit failed")
