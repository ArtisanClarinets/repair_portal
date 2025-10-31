# Path: repair_portal/repair_portal/doctype/technician_availability/technician_availability.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Technician Availability - manages technician scheduling and availability tracking.
# Dependencies: frappe, user management, scheduling

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class TechnicianAvailability(Document):
    """
    Controller for Technician Availability DocType.
    Manages technician scheduling and availability.
    """

    def validate(self):
        """Validate availability requirements."""
        if not self.technician:
            frappe.throw(_("Technician is required"))
            
        if not self.date:
            frappe.throw(_("Date is required"))
            
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            frappe.throw(_("End time must be after start time"))
            
    def before_save(self):
        """Calculate availability hours."""
        if self.start_time and self.end_time:
            start = frappe.utils.get_datetime(f"{self.date} {self.start_time}")
            end = frappe.utils.get_datetime(f"{self.date} {self.end_time}")
            delta = end - start
            self.total_hours = delta.total_seconds() / 3600