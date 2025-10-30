# Path: repair_portal/repair_portal/doctype/vendor_turnaround_log/vendor_turnaround_log.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Vendor Turnaround Log - tracks vendor performance and turnaround times for outsourced repair work.
# Dependencies: frappe, vendor management, repair tracking

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class VendorTurnaroundLog(Document):
    """
    Controller for Vendor Turnaround Log DocType.
    Tracks vendor performance and turnaround times.
    """

    def validate(self):
        """Validate vendor log requirements."""
        if not self.vendor:
            frappe.throw(_("Vendor is required"))
            
        if self.start_date and self.end_date and self.end_date < self.start_date:
            frappe.throw(_("End date cannot be before start date"))
            
    def before_save(self):
        """Calculate turnaround time."""
        if self.start_date and self.end_date:
            delta = frappe.utils.get_datetime(self.end_date) - frappe.utils.get_datetime(self.start_date)
            self.turnaround_days = delta.days