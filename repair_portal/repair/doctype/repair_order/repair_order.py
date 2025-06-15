# File: repair_portal/repair/doctype/repair_order/repair_order.py
# Updated: 2025-06-15
# Version: 1.0
# Purpose: Server-side logic for Repair Order DocType

import frappe
from frappe.model.document import Document

class RepairOrder(Document):
    def validate(self):
        if not self.intake:
            frappe.throw("Intake reference is required.")

    def on_submit(self):
        frappe.msgprint("Repair Order has been submitted.")