# Path: repair_portal/repair_portal/instrument_setup/doctype/clarinet_template_task/clarinet_template_task.py
# Version: v1.0
# Date: 2025-08-12
# Purpose: Child rows on Setup Template used to seed Clarinet Setup Task docs.
# Copyright (c) 2025, DT and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ClarinetTemplateTask(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		test: DF.Attach | None
	# end: auto-generated types
	pass
