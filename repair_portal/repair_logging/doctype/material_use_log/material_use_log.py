# ---------------------------------------------------------------------------
# File: repair_portal/repair_logging/doctype/material_use_log/material_use_log.py
# Date Updated: 2025-07-02
# Version: v1.2
# Purpose: Enforces validation and decrements stock when material is used.
# ---------------------------------------------------------------------------

import frappe
from frappe import _
from frappe.model.document import Document

class MaterialUseLog(Document):

    def validate(self):
        if self.qty <= 0:
            frappe.throw(_("Quantity must be greater than zero."))

        if not frappe.db.exists("Item", self.item_code):
            frappe.throw(_("Item {0} does not exist.").format(self.item_code))

    def on_submit(self):
        # Create a Stock Entry to deduct material
        stock_entry = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Issue",
            "items": [
                {
                    "item_code": self.item_code,
                    "qty": self.qty,
                    "uom": self.uom,
                    "s_warehouse": self.source_warehouse,
                }
            ]
        })
        stock_entry.insert(ignore_permissions=True)
        stock_entry.submit()