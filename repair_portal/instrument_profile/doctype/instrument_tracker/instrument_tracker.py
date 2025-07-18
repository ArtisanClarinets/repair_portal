# File: instrument_profile/doctype/instrument_tracker/instrument_tracker.py
# Updated: 2025-07-14
# Version: 1.1
# Purpose: Backend controller for Instrument Tracker. Aggregates logs and data for a given instrument profile.

import frappe
from frappe.model.document import Document


class InstrumentTracker(Document):
    def onload(self):
        """
        Aggregates all service, repair, and inspection logs for the linked instrument profile,
        and exposes them as dashboard data on the client side.
        """
        serial = self.serial_no
        if not serial:
            return

        # PATCH: Ensure serial_no exists in ERPNext Serial No
        if not frappe.db.exists('Serial No', serial):
            frappe.throw(f"Serial No '{serial}' does not exist in ERPNext!")

        # Aggregate Service Logs
        service_logs = frappe.get_all(
            'Service Log',
            filters={'serial_no': serial},
            fields=['name', 'date', 'service_type', 'description', 'performed_by', 'notes'],
        )
        # Aggregate Inspection Logs
        inspection_logs = frappe.get_all(
            'Clarinet Inspection',
            filters={'serial_no': serial},
            fields=['name', 'inspection_date', 'inspected_by', 'overall_condition', 'notes'],
        )
        # Additional related records can be fetched here
        # Add aggregated data to __onload for JS access
        self.set_onload('service_logs', service_logs)
        self.set_onload('inspection_logs', inspection_logs)
