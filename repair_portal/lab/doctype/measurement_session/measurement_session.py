# File: repair_portal/repair_portal/lab/doctype/measurement_session/measurement_session.py
# Updated: 2025-06-28
# Version: 1.0
# Purpose: Server-side logic for Measurement Session doctype

import frappe
from frappe.model.document import Document


class MeasurementSession(Document):
	def validate(self):
		if not self.instrument:
			frappe.throw("Instrument is required.")
