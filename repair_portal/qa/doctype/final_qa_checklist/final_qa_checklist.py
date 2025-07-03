# ---------------------------------------------------------------------------
# File: repair_portal/qa/doctype/final_qa_checklist/final_qa_checklist.py
# Date Updated: 2025-07-02
# Version: v1.2
# Purpose: Validates QA checklist completion and updates Instrument Profile status.
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
        if self.instrument_profile:
            frappe.db.set_value("Instrument Profile", self.instrument_profile, "status", "QA Complete")
