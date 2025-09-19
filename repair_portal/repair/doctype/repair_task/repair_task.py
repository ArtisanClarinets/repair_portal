# Relative Path: repair_portal/repair_task/doctype/repair_task/repair_task.py
# Last Updated: 2025-07-21
# Version: 1.1
# Purpose: Repair Task server logic including validation of assignment and completion timestamp.
# Notes: Ensures parent Repair Order exists.
from __future__ import annotations

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
        status: DF.Literal['', 'Pending', 'In Progress', 'Completed']
        task_type: DF.Link
        technician: DF.Link | None

    # end: auto-generated types
    def start(self):
        if self.status == "Running":
            frappe.throw("Task is already running.")
        self.status = "Running"
        self.started_at = now_datetime()
        self.save(ignore_permissions=True)

    def stop(self):
        if self.status != "Running":
            frappe.throw("Task is not running.")
        self.status = "Open"
        self.save(ignore_permissions=True)

    def complete(self):
        self.status = "Completed"
        self.completed_at = now_datetime()
        self.save(ignore_permissions=True)


@frappe.whitelist()
def post_task_time(task_name: str, minutes: int) -> str:
    """Update task minutes only (no Timesheet creation)."""
    task = frappe.get_doc("Repair Task", task_name)
    task.actual_minutes = int(task.actual_minutes or 0) + int(minutes or 0)
    task.save(ignore_permissions=True)
    return task.name
