# File: repair_portal/repair_portal/doctype/custom_doctype/custom_doctype.py
# Updated: 2025-06-09
# Version: 1.0
# Purpose: Server-side logic for Custom Doctype

import frappe
from frappe.model.document import Document


class CustomDoctype(Document):
    def validate(self):
        if not self.customer:
            frappe.throw("Customer is required")

    def on_submit(self):
        frappe.msgprint("Document submitted.")