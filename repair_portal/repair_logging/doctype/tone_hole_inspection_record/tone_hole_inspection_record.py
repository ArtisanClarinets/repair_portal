# File Header Template
# Relative Path: repair_portal/repair_logging/doctype/tone_hole_inspection_record/tone_hole_inspection_record.py
# Last Updated: 2025-07-06
# Version: v1.0
# Purpose: Child table for documenting tone hole visual inspection results.
# Dependencies: frappe

import frappe
from frappe import _
from frappe.model.document import Document


class ToneHoleInspectionRecord(Document):
	def validate(self):
		"""Ensure each tone hole record is fully documented."""
		if not self.tone_hole_number:
			frappe.throw(_("Tone Hole Number is required."))

		if not self.visual_status:
			frappe.throw(_("Visual Status (Clean, Damaged, etc.) is required."))

		if not self.photo:
			frappe.throw(_("Photo attachment is required for each tone hole inspection."))
