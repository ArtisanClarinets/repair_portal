# File: repair_portal/repair_logging/doctype/repair_parts_used/repair_parts_used.py
# Updated: 2025-07-19
# Version: 1.1
# Purpose: Track parts used in repairs, including item details and quantities
# This module is part of the Repair Portal application for Frappe/ERPNext
# It extends the Document class to provide custom functionality for repair part tracking
from __future__ import annotations
import frappe
from frappe.model.document import Document
from frappe.utils import flt


class RepairPartsUsed(Document):
	"""
	Controller for tracking parts used in repair operations.
	Links to repair orders and maintains inventory accuracy.
	"""

	def validate(self):
		"""Validate part usage and availability."""
		if not self.item_code: # type: ignore
			frappe.throw("Item Code is required")

		if not self.qty or flt(self.qty) <= 0: # type: ignore
			frappe.throw("Quantity must be greater than 0")

		# Calculate amount if rate is provided
		if self.rate and self.qty: # type: ignore
			self.amount = flt(self.qty) * flt(self.rate) # type: ignore

		# Validate against available inventory
		if self.item_code: # type: ignore
			self.validate_inventory_availability()

	def validate_inventory_availability(self):
		"""Check if sufficient inventory is available."""
		try:
			available_qty = (
				frappe.db.get_value(
					"Bin",
					{"item_code": self.item_code, "warehouse": self.warehouse or "Stores - AC"}, # type: ignore
				)
				or 0
			)

			if flt(self.qty) > flt(available_qty): # type: ignore
				frappe.msgprint(
					f"Warning: Requested quantity ({self.qty}) exceeds available stock ({available_qty}) for {self.item_name or self.item_code}", # type: ignore
					alert=True,
				)
		except Exception as e:
			frappe.log_error(f"Error validating inventory for {self.item_code}: {str(e)}") # type: ignore

	def on_submit(self):
		"""Update inventory levels when part usage is confirmed."""
		if self.item_code and self.qty: # type: ignore
			self.create_stock_entry()

	def create_stock_entry(self):
		"""Create stock entry to reduce inventory for used parts."""
		try:
			stock_entry = frappe.get_doc(
				{ # type: ignore
					"doctype": "Stock Entry",
					"stock_entry_type": "Material Issue",
					"purpose": "Material Issue",
					"reference_doctype": "Repair Parts Used",
					"reference_docname": self.name,
					"items": [
						{
							"item_code": self.item_code, # type: ignore
							"qty": self.qty, # type: ignore
							"s_warehouse": self.warehouse or "Stores - AC", # type: ignore
							"cost_center": "Main - AC",
						}
					],
				}
			)
			stock_entry.submit()

			frappe.msgprint(f"Stock Entry {stock_entry.name} created for part usage")

		except Exception as e:
			frappe.log_error(f"Failed to create stock entry for {self.name}: {str(e)}")
			frappe.throw("Failed to update inventory. Please contact system administrator.")
