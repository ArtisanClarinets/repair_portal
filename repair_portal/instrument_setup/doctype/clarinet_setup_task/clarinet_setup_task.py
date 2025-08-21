# Path: repair_portal/repair_portal/instrument_setup/doctype/clarinet_setup_task/clarinet_setup_task.py
# Version: v1.3
# Date: 2025-08-12
# Purpose: Projects-like Task with dependency gating and parent-progress roll-up.

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class ClarinetSetupTask(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from repair_portal.instrument_setup.doctype.clarinet_task_depends_on.clarinet_task_depends_on import (
			ClarinetTaskDependsOn,
		)

		actual_end: DF.Datetime | None
		actual_start: DF.Datetime | None
		amended_from: DF.Link | None
		assigned_to: DF.Link | None
		clarinet_initial_setup: DF.Link | None
		color: DF.Color | None
		depends_on: DF.Table[ClarinetTaskDependsOn]
		description: DF.TextEditor | None
		exp_end_date: DF.Date | None
		exp_start_date: DF.Date | None
		instrument: DF.Link | None
		is_group: DF.Check
		parent_task: DF.Link | None
		priority: DF.Literal["Low", "Medium", "High", "Urgent"]
		progress: DF.Percent
		sequence: DF.Int
		serial: DF.Link | None
		status: DF.Literal["Open", "Working", "Paused", "Pending Review", "Completed", "Canceled"]
		subject: DF.Data

	# end: auto-generated types
	def validate(self):
		# Sanity: date ranges
		if self.exp_start_date and self.exp_end_date and self.exp_end_date < self.exp_start_date: # type: ignore
			frappe.throw(_("Expected End cannot be earlier than Expected Start."))

		# Dependency gating: cannot start/complete if predecessors not Completed
		if self.status in {"Working", "Pending Review", "Completed"}:
			if self.depends_on:
				pending = []
				for dep in self.depends_on:
					st = frappe.db.get_value("Clarinet Setup Task", dep.task, "status")
					if st != "Completed":
						pending.append(f"{dep.task} ({st})")
				if pending:
					frappe.throw(_("This task depends on unfinished tasks: {0}").format(", ".join(pending)))

		# Auto progress on Completed
		if self.status == "Completed":
			self.progress = 100

		# Actual times quality-of-life
		if self.status == "Working" and not self.actual_start:
			self.actual_start = now_datetime()
		if self.status == "Completed" and not self.actual_end:
			self.actual_end = now_datetime()

	def on_update(self):
		# Bubble up progress to parent
		if self.clarinet_initial_setup:
			try:
				frappe.enqueue(
					"repair_portal.repair_portal.instrument_setup.doctype.clarinet_initial_setup.clarinet_initial_setup.update_parent_progress",
					initial_setup=self.clarinet_initial_setup,
					queue="short",
				)
			except Exception:
				# Fallback if queue not available
				update_parent_progress_inline(self.clarinet_initial_setup)

	def on_trash(self):
		if self.clarinet_initial_setup:
			update_parent_progress_inline(self.clarinet_initial_setup)


def update_parent_progress_inline(initial_setup: str):
	"""Inline (non-queued) parent progress roll-up fallback."""
	tasks = frappe.get_all(
		"Clarinet Setup Task",
		filters={"clarinet_initial_setup": initial_setup},
		fields=["name", "progress"],
	)
	if not tasks:
		frappe.db.set_value("Clarinet Initial Setup", initial_setup, "progress", 0)
		return
	avg = round(sum((t.get("progress") or 0) for t in tasks) / len(tasks), 2)
	frappe.db.set_value("Clarinet Initial Setup", initial_setup, "progress", avg)
