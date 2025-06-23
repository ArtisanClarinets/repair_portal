# File: repair_logging/doctype/service_log/service_log.py
# Updated: 2025-06-14
# Version: 1.0
# Purpose: Backend logic for Service Log doctype. Used for instrument service, repair, maintenance, and other logging events.

import frappe
from frappe.model.document import Document


class ServiceLog(Document):
    def validate(self):
        # Ensure basic service log data integrity
        if not self.instrument_profile:
            frappe.throw('Instrument Profile is required.')
        if not self.description:
            frappe.throw('Service description is required.')

    def on_submit(self):
        frappe.msgprint(f'Service log for {self.instrument_profile} submitted.')
