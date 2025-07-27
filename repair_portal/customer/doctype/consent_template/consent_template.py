# Copyright (c) 2025, DT and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ConsentTemplate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		consent_type: DF.Literal["Sales", "Repair", "Custom", "Privacy", "Shipping", "Health"]
		content: DF.TextEditor
		is_active: DF.Check
		title: DF.Data
		valid_from: DF.Date | None
		valid_upto: DF.Date | None
		version: DF.Int
	# end: auto-generated types
	pass
