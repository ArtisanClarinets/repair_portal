# File: repair_portal/service_planning/doctype/repair_estimate/repair_estimate.py
# Updated: 2025-06-16
# Version: 1.0
# Purpose: Main estimate document for planning service labor + parts

from frappe.model.document import Document


class RepairEstimate(Document):
    def validate(self):
        total = 0
        for item in self.line_items:
            if item.hours and item.rate:
                item.amount = item.hours * item.rate
                total += item.amount
        self.total_cost = total