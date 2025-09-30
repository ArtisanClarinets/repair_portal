# -*- coding: utf-8 -*-
# Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/intake/doctype/intake_accessory_item/intake_accessory_item.py
# Last Updated: 2025-09-19
# Version: v1.2.0 (Amount calc, auto-fetch UOM/description/rate)
# Purpose:
#   Child row controller for Clarinet Intake accessories & included parts.
#   • qty default = 1, non-negative guard
#   • auto-fill description & UOM from Item when missing
#   • auto-fill selling rate from Item Price (using Intake Settings price list) when missing
#   • compute amount = qty * rate
# Dependencies:
#   - frappe (v15)
#   - ERPNext present with Item Price
#   - Clarinet Intake Settings (for selling_price_list)

from __future__ import annotations

from typing import Optional

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

# Use the settings from the moved module path
from repair_portal.repair_portal_settings.doctype.clarinet_intake_settings.clarinet_intake_settings import (
	get_intake_settings,
)


class IntakeAccessoryItem(Document):
	"""
	Accessories/parts line for Clarinet Intake.
	"""

	# ----------------------------------------------------------------------
	# Lifecycle
	# ----------------------------------------------------------------------
	def validate(self) -> None:
		self._ensure_defaults()
		self._autofill_from_item()
		self._ensure_rate()
		self._compute_amount()

	# ----------------------------------------------------------------------
	# Helpers
	# ----------------------------------------------------------------------
	def _ensure_defaults(self) -> None:
		"""Establish safe defaults and guards."""
		if self.qty is None:
			self.qty = 1
		if flt(self.qty) < 0:
			frappe.throw(_("Qty cannot be negative."))
		# description/uom handled in _autofill_from_item()

	def _autofill_from_item(self) -> None:
		"""Populate description & UOM from the linked Item when missing."""
		if not self.item_code:
			return

		item = frappe.db.get_value(
			"Item", self.item_code, ["description", "stock_uom", "item_name"], as_dict=True
		)
		if not item:
			return

		if not self.description:
			# Prefer the rich Item.description; fallback to item_name if empty
			self.description = item.get("description") or item.get("item_name")

		if not self.uom and item.get("stock_uom"):
			self.uom = item.get("stock_uom")

	def _ensure_rate(self) -> None:
		"""
		If rate was not provided, try to fetch the selling price from Item Price.
		Respects Clarinet Intake Settings.selling_price_list when present.
		"""
		if flt(self.rate):
			return  # keep user-entered rate

		if not self.item_code:
			return

		settings = get_intake_settings()
		price_list = settings.get("selling_price_list") or "Standard Selling"

		# Primary: Item Price on configured selling Price List
		price = frappe.db.get_value(
			"Item Price",
			{"item_code": self.item_code, "price_list": price_list},
			"price_list_rate",
		)

		# Fallback: any selling Item Price for this item
		if price is None:
			price = frappe.db.get_value(
				"Item Price",
				{"item_code": self.item_code, "selling": 1},
				"price_list_rate",
			)

		if price is not None:
			self.rate = flt(price)

	def _compute_amount(self) -> None:
		"""amount = qty * rate (currency-safe with flt)."""
		self.amount = flt(self.qty) * flt(self.rate or 0)
