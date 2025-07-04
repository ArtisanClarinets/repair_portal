# Relative Path: repair_portal/repair_task/doctype/repair_task/repair_task.py
# Last Updated: 2025-07-03
# Version: 1.0
# Purpose: Repair Task server logic including validation of assignment and completion timestamp.
# Notes: Ensures parent Repair Order exists.

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class RepairTask(Document):
    def validate(self):
        if not self.repair_order:
            frappe.throw("Repair Order reference is required.")

        if not frappe.db.exists("Repair Order", self.repair_order):
            frappe.throw(f"Repair Order '{self.repair_order}' not found.")

        if not self.assigned_to:
            frappe.throw("Assigned To is required.")

    def before_save(self):
        if self.status == "Completed" and not self.completed_on:
            self.completed_on = now_datetime()