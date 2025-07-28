# Copyright (c) 2025, DT and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class InstrumentModel(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		body_material: DF.Data | None
		bore_type: DF.Data | None
		brand: DF.Link
		instrument_type: DF.Link | None
		model: DF.Data
	# end: auto-generated types
	pass
