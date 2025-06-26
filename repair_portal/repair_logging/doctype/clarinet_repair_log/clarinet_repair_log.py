# File: repair_portal/repair_logging/doctype/clarinet_repair_log/clarinet_repair_log.py
# Updated: 2025-06-16
# Version: 1.1
# Purpose: Auto-fill material usage from scanned barcodes or linked pad condition

import frappe
from frappe.model.document import Document


class ClarinetRepairLog(Document):
    def after_insert(self):
        """Create a Service Order Tracker after the first save."""
        if not frappe.db.exists("Service Order Tracker", {"repair_log": self.name}):
            tracker = frappe.new_doc("Service Order Tracker")
            tracker.repair_log = self.name
            tracker.current_stage = "Estimate Sent"
            tracker.insert(ignore_permissions=True)

    def on_update(self):
        self.auto_add_materials_from_barcode()

    def auto_add_materials_from_barcode(self):
        barcode_logs = frappe.get_all(
            "Barcode Scan Entry", filters={"reference_name": self.name}, fields=["barcode"]
        )
        for log in barcode_logs:
            item = frappe.db.get_value("Item", {"barcode": log.barcode}, ["name"])
            if item:
                self.append("material_usage", {"item_code": item, "qty": 1})
