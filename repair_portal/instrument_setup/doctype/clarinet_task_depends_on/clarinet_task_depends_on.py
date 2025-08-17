# Path: repair_portal/repair_portal/instrument_setup/doctype/clarinet_task_depends_on/clarinet_task_depends_on.py
# Version: v1.0
# Date: 2025-08-12
# Purpose: Child table; logic lives in ClarinetSetupTask.validate
# Copyright (c) 2025, DT and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ClarinetTaskDependsOn(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		task: DF.Link
	# end: auto-generated types
	pass
