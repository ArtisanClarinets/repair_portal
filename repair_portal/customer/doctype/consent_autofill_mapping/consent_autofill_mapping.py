# Copyright (c) 2025, Dylan Thompson and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ConsentAutofillMapping(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		enabled: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types
	pass
