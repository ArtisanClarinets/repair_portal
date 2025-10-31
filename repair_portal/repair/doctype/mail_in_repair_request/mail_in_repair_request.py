# Path: repair_portal/repair_portal/doctype/mail_in_repair_request/mail_in_repair_request.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Mail In Repair Request - manages mail-in repair requests.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class MailInRepairRequest(Document):
    """Controller for Mail In Repair Request documents."""

    def validate(self):
        """Validate mail-in repair request requirements."""
        if not self.customer:
            frappe.throw(_("Customer is required"))
        if not self.instrument_description:
            frappe.throw(_("Instrument Description is required"))