# File: repair_portal/repair_portal/repair/doctype/repair_issue/repair_issue.py
# Updated: 2025-06-28
# Version: 1.1
# Purpose: Server-side logic for Repair Issue doctype

import frappe
from frappe.model.document import Document

class RepairIssue(Document):
    def autoname(self):
        if self.customer:
            self.name = f"{self.customer}-{frappe.utils.nowdate()}"

    def validate(self):
        if not self.customer:
            frappe.throw("Customer is required")

    def on_submit(self):
        frappe.msgprint("Repair Issue submitted.")