# File: repair_portal/stock/doctype/stock_entry/stock_entry.py
# Purpose: Auto-create Inspection Report on Stock Entry submit if QC is required
# Compatible: ERPNext v15, class-based event override

import frappe
from frappe.model.document import Document


class StockEntry(Document):
    def on_submit(self):
        for item in self.items:
            if item.get("qc_required"):
                # PATCH: Ensure serial_no exists in ERPNext Serial No
                if not frappe.db.exists("Serial No", item.serial_no):
                    frappe.throw(f"Serial No '{item.serial_no}' does not exist in ERPNext!")
                # Prevent duplicate reports for the same serial/stock entry
                exists = frappe.db.exists(
                    "Inspection Report", {"serial_no": item.serial_no, "stock_entry": self.name}
                )
                if not exists:
                    doc = frappe.new_doc("Inspection Report")
                    doc.instrument_id = item.item_code
                    doc.serial_no = item.serial_no
                    doc.stock_entry = self.name
                    doc.status = "Scheduled"
                    doc.inspection_type = "Clarinet QA"
                    doc.customer_name = getattr(self, "customer", "")
                    doc.save(ignore_permissions=True)
                    frappe.msgprint(f"Inspection Report auto-created for Serial: {item.serial_no}")
