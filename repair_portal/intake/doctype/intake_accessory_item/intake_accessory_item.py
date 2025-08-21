# Relative Path: repair_portal/intake/doctype/intake_accessory_item/intake_accessory_item.py
# Last Updated: 2025-07-04
# Version: v1.0
# Purpose: Validation and lifecycle hooks for Accessories Checklist entries
# Dependencies: Frappe Framework >= v15

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class IntakeAccessoryItem(Document):
	"""
	Accessories Checklist Row Controller
	"""

	accessory: str
	quantity: int
	notes: str

	def validate(self) -> None:
		"""
		Validation before saving the accessory row.
		"""
		if not self.accessory:
			frappe.throw(_("Accessory description cannot be empty."))

		if self.quantity is None:
			self.quantity = 1

		if self.quantity < 0:
			frappe.throw(_("Quantity cannot be negative."))

		if self.quantity == 0:
			frappe.msgprint(_("Warning: Quantity is set to zero. Consider updating if this is unintended."))
