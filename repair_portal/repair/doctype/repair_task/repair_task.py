# Relative Path: repair_portal/repair_task/doctype/repair_task/repair_task.py
# Last Updated: 2025-07-21
# Version: 1.1
# Purpose: Repair Task server logic including validation of assignment and completion timestamp.
# Notes: Ensures parent Repair Order exists.

# begin: auto-generated types
# This code is auto-generated. Do not touch it – Frappe will overwrite.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from frappe.types import DF

	repair_order: DF.Link
	assigned_to: DF.Link
	status: DF.Select
	completed_on: DF.Datetime | None
# end: auto-generated types

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class RepairTask(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from repair_portal.instrument_profile.doctype.instrument_photo.instrument_photo import (
			InstrumentPhoto,
		)

		actual_hours: DF.Float
		description: DF.Text | None
		est_hours: DF.Float
		images: DF.Table[InstrumentPhoto]
		log: DF.Link | None
		long_description: DF.TextEditor | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		parts_cost: DF.Currency
		remarks: DF.SmallText | None
		status: DF.Literal["", "Pending", "In Progress", "Completed"]
		task_type: DF.Link
		technician: DF.Link | None

	# end: auto-generated types
	def validate(self):
		if not self.repair_order:  # type: ignore
			frappe.throw("Repair Order reference is required.")

		if not frappe.db.exists("Repair Order", self.repair_order):  # type: ignore
			frappe.throw(f"Repair Order '{self.repair_order}' not found.")  # type: ignore

		if not self.assigned_to:  # type: ignore
			frappe.throw("Assigned To is required.")  # type: ignore

	def before_save(self):
		if self.status == "Completed" and not self.completed_on:  # type: ignore
			self.completed_on = now_datetime()
