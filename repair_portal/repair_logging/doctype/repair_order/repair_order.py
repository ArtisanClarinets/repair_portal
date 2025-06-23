# File: repair_portal/repair_portal/repair_logging/doctype/repair_order/repair_order.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Handles Repair Order logic including validation and lifecycle events

import frappe
from frappe.model.document import Document


class RepairOrder(Document):
    def validate(self):
        if not self.customer or not self.instrument:
            frappe.throw("Customer and Instrument must be specified.")