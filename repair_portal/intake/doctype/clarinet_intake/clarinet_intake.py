from __future__ import annotations

# File Header Template
# Relative Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# Last Updated: 2025-07-13
# Version: v1.7
# Purpose: Handles Clarinet Intake submission logic, including auto-creation of Instrument Profile and Quality Inspection on Inventory intake.
# Dependencies: Instrument Profile, Quality Inspection, frappe.throw

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class ClarinetIntake(Document):
	def on_submit(self):
		if self.intake_type == "Inventory":
			# Field assertions
			missing = [f for f in ["serial_number", "brand", "model", "instrument_type"] if not getattr(self, f)]
			if missing:
				frappe.throw(f"Missing required fields for Inventory Intake: {', '.join(missing)}")

			# Enforce known user
			owner = self.received_by

			instrument = frappe.get_doc({
				"doctype": "Instrument Profile",
				"serial_number": self.serial_number,
				"brand": self.brand,
				"model": self.model,
				"instrument_type": self.instrument_type,
				"linked_intake": self.name
			})
			instrument.owner = owner
			instrument.insert()

			if not instrument.name:
				frappe.throw("Instrument Profile creation failed.")

			inspection = frappe.get_doc({
				"doctype": "Quality Inspection",
				"reference_type": "Instrument Profile",
				"reference_name": instrument.name,
				"inspection_type": "Incoming",
				"report_date": nowdate()
			})
			inspection.owner = owner
			inspection.insert()

			if not inspection.name:
				frappe.throw("Quality Inspection creation failed.")