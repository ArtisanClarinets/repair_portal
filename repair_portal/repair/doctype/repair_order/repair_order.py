# repair_portal/repair/doctype/repair_order/repair_order.py
# Updated: 2025-06-15
# Version: 1.2
# Purpose: Warranty logic – technician alert + billing exemption

import frappe
from frappe.model.document import Document
from frappe import _

class RepairOrder(Document):
    def before_save(self):
        if self.instrument_profile:
            ip = frappe.get_doc("Instrument Profile", self.instrument_profile)
            if ip.warranty_active:
                self.is_warranty = 1
                self.append("comments", {"comment": _("This repair is under WARRANTY – do not bill labor unless approved.")})
                self.total_parts_cost = 0
                self.total_labor_hours = 0
            else:
                self.is_warranty = 0