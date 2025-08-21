# ---------------------------------------------------------------------------
# File: repair_portal/repair_logging/doctype/material_use_log/material_use_log.py
# Date Updated: 2025-07-02
# Version: v1.2
# Purpose: Enforces validation and decrements stock when material is used.
# ---------------------------------------------------------------------------
from __future__ import annotations
import frappe
from frappe import _
from frappe.model.document import Document


class MaterialUseLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		item_name: DF.Link
		operation_link: DF.DynamicLink | None
		operation_type: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qty: DF.Float
		remarks: DF.SmallText | None
		source_warehouse: DF.Link | None
		used_on: DF.Data | None

	# end: auto-generated types
	def validate(self):
		if self.qty <= 0:
			frappe.throw(_("Quantity must be greater than zero."))

		if not frappe.db.exists("Item", self.item_code): # type: ignore
			frappe.throw(_("Item {0} does not exist.").format(self.item_code)) # type: ignore

	def on_submit(self):
		# Create a Stock Entry to deduct material
		stock_entry = frappe.get_doc(
			{
				"doctype": "Stock Entry",
				"stock_entry_type": "Material Issue",
				"items": [
					{
						"item_code": self.item_code, # type: ignore
						"qty": self.qty,
						"uom": self.uom, # type: ignore
						"s_warehouse": self.source_warehouse,
					}
				],
			}
		)
		stock_entry.insert(ignore_permissions=True)
		stock_entry.submit()
