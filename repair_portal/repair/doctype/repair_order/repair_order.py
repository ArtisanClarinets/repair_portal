# repair_portal/repair/doctype/repair_order/repair_order.py
# Last Updated: 2025-07-14
# Version: v2.0
# Purpose: Unified controller logic for Repair Order (merging Repair Request)
# Dependencies: Instrument Profile, Repair Note, Qa Checklist Item, Customer, User

import frappe
from frappe import _
from frappe.model.document import Document

class RepairOrder(Document):
    def validate(self):
        # Ensure customer is present
        if not self.customer:
            frappe.throw(_("Customer is required."))
        # Ensure issue_description is present
        if not self.issue_description:
            frappe.throw(_("Issue Description is required."))

    def before_save(self):
        # Existing warranty logic
        if hasattr(self, 'instrument_profile') and self.instrument_profile:
            ip = frappe.get_doc("Instrument Profile", self.instrument_profile)
            if hasattr(ip, 'warranty_active') and ip.warranty_active:
                self.is_warranty = 1
                self.append(
                    "comments",
                    {"comment": _("This repair is under WARRANTY – do not bill labor unless approved.")},
                )
                self.total_parts_cost = 0
                self.total_labor_hours = 0
            else:
                self.is_warranty = 0

    def on_submit(self):
        # Informative user feedback
        frappe.msgprint(_("Repair Order submitted."))
