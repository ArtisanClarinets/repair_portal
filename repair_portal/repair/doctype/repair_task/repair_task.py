# File: repair_portal/repair/doctype/repair_task/repair_task.py
# Updated: 2025-06-15
# Version: 1.0
# Purpose: Controller for Repair Task child table

import frappe
from frappe.model.document import Document


class RepairTask(Document):
    def validate(self):
        if not self.task_type:
            frappe.throw("Task type is required for each Repair Task.")
