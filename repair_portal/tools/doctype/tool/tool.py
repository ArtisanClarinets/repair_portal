# File: repair_portal/tools/doctype/tool/tool.py
# Date Updated: 2025-06-12
# Version: v1.0
# Purpose: Tracks tool metadata, serviceability, and calibration lifecycle.

import frappe
from frappe.model.document import Document


class Tool(Document):
    def validate(self):
        if self.requires_calibration and not self.next_due:
            frappe.throw("Please set 'Next Calibration Due' for tools requiring calibration.")
