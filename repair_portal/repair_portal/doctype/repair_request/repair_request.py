# Path: repair_portal/repair_portal/doctype/repair_request/repair_request.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Repair Request - manages repair service requests.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class RepairRequest(Document):
    """Controller for Repair Request documents."""

    def validate(self):
        """Validate repair request requirements."""
        if not self.customer:
            frappe.throw(_("Customer is required"))
        if not self.instrument:
            frappe.throw(_("Instrument is required"))