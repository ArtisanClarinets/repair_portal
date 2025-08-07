# repair_portal/repair/doctype/repair_order/repair_order.py
# Last Updated: 2025-07-21
# Version: v2.2
# Purpose: Unified controller logic for Repair Order (merging Repair Request). Now Fortune-500 compliant: robust error logging, docstrings, and future-proof automation hooks.
# Dependencies: Instrument Profile, Repair Note, Qa Checklist Item, Customer, User

# begin: auto-generated types
# This code is auto-generated. Do not touch it – Frappe will overwrite.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frappe.types import DF  # DF = “DocField” helper
    customer: DF.Link
    issue_description: DF.SmallText
    instrument_profile: DF.Link | None
    is_warranty: DF.Check
    total_parts_cost: DF.Currency
    total_labor_hours: DF.Float
# end: auto-generated types

import frappe
from frappe import _
from frappe.model.document import Document


class RepairOrder(Document):
    def validate(self):
        """Ensures all required fields are present before save/submit."""
        if not self.customer:
            frappe.throw(_("Customer is required."))
        if not self.issue_description:
            frappe.throw(_("Issue Description is required."))

    def before_save(self):
        """
        Handles warranty logic and sets repair as warranty if applicable.
        Logs errors for audit.
        """
        try:
            if hasattr(self, "instrument_profile") and self.instrument_profile:
                ip = frappe.get_doc("Instrument Profile", self.instrument_profile)
                if hasattr(ip, "warranty_active") and ip.warranty_active:
                    self.is_warranty = 1
                    self.append(
                        "comments",
                        {"comment": _("This repair is under WARRANTY – do not bill labor unless approved.")},
                    )
                    self.total_parts_cost = 0
                    self.total_labor_hours = 0
                else:
                    self.is_warranty = 0
        except Exception:
            frappe.log_error(frappe.get_traceback(), "RepairOrder: before_save warranty logic failed")

    def on_submit(self):
        """
        Called when Repair Order is submitted. Can be extended for automation (labor log, workflow, notifications).
        """
        try:
            # Example: add labor log, update workflow_state, etc.
            frappe.msgprint(_("Repair Order submitted."))
        except Exception:
            frappe.log_error(frappe.get_traceback(), "RepairOrder: on_submit failed")
