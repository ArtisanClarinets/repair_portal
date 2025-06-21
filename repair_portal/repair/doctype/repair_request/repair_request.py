# File: repair_portal/repair/doctype/repair_request/repair_request.py
# Updated: 2025-06-21
# Version: 1.0
# Purpose: Server-side logic for Repair Request DocType

import frappe
from frappe.model.document import Document

class RepairRequest(Document):
    def validate(self):
        if not self.customer:
            frappe.throw("Customer is required")

    def on_submit(self):
        frappe.msgprint("Repair Request submitted.")