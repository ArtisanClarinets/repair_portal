# File Header Template
# Relative Path: repair_portal/instrument_profile/doctype/instrument_accessory/instrument_accessory.py
# Last Updated: 2025-07-21
# Version: v1.0
# Purpose: Child table for Instrument Accessories (paired, acquired/removed, desc)
# Dependencies: None

# Path: repair_portal/instrument_profile/doctype/instrument_accessory/instrument_accessory.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Child table for instrument accessories (cases, mouthpieces, etc.); tracks acquisition and removal dates
# Dependencies: frappe

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class InstrumentAccessory(Document):
    def validate(self):
        """Validate date logic and current status"""
        # Ensure removed_date is after acquired_date
        if self.removed_date and self.acquired_date:
            if getdate(self.removed_date) < getdate(self.acquired_date):
                frappe.throw(_("Removed Date cannot be before Acquired Date"))

        # If removed_date is set, current should be unchecked
        if self.removed_date and self.current:
            frappe.msgprint(
                _(
                    "Accessory has a removal date but is marked as Currently Paired. Unchecking current status."
                ),
                indicator="orange",
                alert=True,
            )
            self.current = 0
