# File: repair_portal/repair_portal/doctype/repair_request/repair_request.py
# Updated: 2025-06-16
# Version: 1.0
# Purpose: Server-side logic for Repair Request Doctype

import frappe
from frappe.model.document import Document


class RepairRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from repair_portal.repair_logging.doctype.repair_task_log.repair_task_log import (
			RepairTaskLog,
		)
		from repair_portal.repair_portal.doctype.qa_checklist_item.qa_checklist_item import (
			QaChecklistItem,
		)

		amended_from: DF.Link | None
		customer: DF.Link
		date_reported: DF.Date | None
		instrument_category: DF.Link | None
		issue_description: DF.Text
		priority_level: DF.Literal["", "Low", "Medium", "High"]
		promise_date: DF.Date | None
		qa_checklist: DF.Table[QaChecklistItem]
		repair_notes: DF.Table[RepairTaskLog]
		status: DF.Literal["", "Open", "In Progress", "Resolved", "Closed"]
		technician_assigned: DF.Link | None

	# end: auto-generated types
	def validate(self):
		if not self.customer:
			frappe.throw("Customer is required")

	def on_submit(self):
		frappe.msgprint("Repair Request submitted.")
