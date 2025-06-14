# File: repair_portal/repair_portal/doctype/custom_doctype/custom_doctype.py
# Updated: 2025-06-14
# Version: 1.1
# Purpose: Server-side logic for Custom Doctype, includes linkage to Instrument Profile

import frappe
from frappe.model.document import Document

class CustomDoctype(Document):
    def validate(self):
        if not self.customer:
            frappe.throw("Customer is required")

        # Ensure instrument profile exists or create it
        if not self.instrument_profile:
            serial = self.issue_description[:12] if self.issue_description else "TEMP"
            instrument = frappe.get_all("Instrument Profile", filters={"serial_number": serial, "customer": self.customer}, limit=1)
            if instrument:
                self.instrument_profile = instrument[0].name
            else:
                doc = frappe.get_doc({
                    "doctype": "Instrument Profile",
                    "serial_number": serial,
                    "customer": self.customer
                })
                doc.insert()
                self.instrument_profile = doc.name

    def on_submit(self):
        frappe.msgprint("Document submitted.")