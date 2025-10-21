# File: repair_portal/repair_portal/repair/doctype/repair_issue/repair_issue.py
# Updated: 2025-06-28
# Version: 1.1
# Purpose: Server-side logic for Repair Issue doctype

from __future__ import annotations

import frappe
from frappe.model.document import Document


class RepairIssue(Document):
    def autoname(self):
        if self.customer:  # type: ignore
            self.name = f"{self.customer}-{frappe.utils.nowdate()}"  # type: ignore

    def validate(self):
        if not self.customer:  # type: ignore
            frappe.throw("Customer is required")

    def on_submit(self):
        frappe.msgprint("Repair Issue submitted.")
