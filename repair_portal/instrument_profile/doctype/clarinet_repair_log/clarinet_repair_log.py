# File: repair_portal/instrument_profile/doctype/clarinet_repair_log/clarinet_repair_log.py
# Updated: 2025-06-16
# Version: 1.1
# Purpose: Auto-generate Service Order Tracker on new repair log

import frappe
from frappe.model.document import Document


class ClarinetRepairLog(Document):
    def after_insert(self):
        if not frappe.db.exists("Service Order Tracker", {"repair_log": self.name}):
            tracker = frappe.new_doc("Service Order Tracker")
            tracker.repair_log = self.name
            tracker.current_stage = "Estimate Sent"
            tracker.insert(ignore_permissions=True)