# repair_portal/repair/doctype/repair_order/repair_order.py
# Last Updated: 2025-07-21
# Version: v2.2
# Purpose: Unified controller logic for Repair Order (merging Repair Request). Now Fortune-500 compliant: robust error logging, docstrings, and future-proof automation hooks.
# Dependencies: Instrument Profile, Repair Note, Qa Checklist Item, Customer, User


import frappe
from frappe import _
from frappe.model.document import Document


class RepairOrder(Document):
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
		client: DF.Link | None
		customer: DF.Link
		date_reported: DF.Date | None
		description: DF.Text | None
		estimated_completion: DF.Date | None
		instrument: DF.Link | None
		instrument_category: DF.Link | None
		issue_description: DF.Text
		priority_level: DF.Literal["", "Low", "Medium", "High"]
		promise_date: DF.Date | None
		qa_checklist: DF.Table[QaChecklistItem]
		repair_notes: DF.Table[RepairTaskLog]
		status: DF.Literal["Open", "In Progress", "Resolved", "Closed", "Completed", "Cancelled"]
		technician_assigned: DF.Link | None
		total_cost: DF.Currency

	# end: auto-generated types
	def validate(self):
		"""Ensures all required fields are present before save/submit."""
		if not self.customer:
			frappe.throw(_("Customer is required."))
		if not self.issue_description:
			frappe.throw(_("Issue Description is required."))

	def before_save(self):
		"""
		Handles warranty logic and sets repair as warranty if applicable.
		Logs errors for audit.
		"""
		try:
			if hasattr(self, "instrument_profile") and self.instrument_profile: # type: ignore
				ip = frappe.get_doc("Instrument Profile", self.instrument_profile) # type: ignore
				if hasattr(ip, "warranty_active") and ip.warranty_active: # type: ignore
					self.is_warranty = 1
					self.append(
						"comments",
						{"comment": _("This repair is under WARRANTY – do not bill labor unless approved.")},
					)
					self.total_parts_cost = 0
					self.total_labor_hours = 0
				else:
					self.is_warranty = 0
		except Exception:
			frappe.log_error(frappe.get_traceback(), "RepairOrder: before_save warranty logic failed")

	def on_submit(self):
		"""
		Called when Repair Order is submitted. Can be extended for automation (labor log, workflow, notifications).
		"""
		try:
			# Example: add labor log, update workflow_state, etc.
			frappe.msgprint(_("Repair Order submitted."))
		except Exception:
			frappe.log_error(frappe.get_traceback(), "RepairOrder: on_submit failed")
