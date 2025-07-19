from __future__ import annotations

import frappe
from frappe import _  # <-- translation helper
from frappe.model.document import Document
from frappe.utils import cint, now_datetime


class PulseUpdate(Document):
    """Single progress update against a Repair Request."""

    def before_insert(self):
        # Ensure timestamp
        if not self.update_time:
            self.update_time = now_datetime()

        # Validate percentage
        if self.percent_complete is not None:
            pc = cint(self.percent_complete)
            if not 0 <= pc <= 100:
                frappe.throw(_("Percent Complete must be between 0 and 100"))
            self.percent_complete = pc


@frappe.whitelist(allow_guest=False, methods=["POST"])
def create_update(
    repair_request: str,
    status: str | None = None,
    details: str | None = None,
    percent_complete: int | None = None,
) -> str:
    """Create a new Pulse Update and notify viewers in real time."""

    frappe.only_for("Technician")

    doc = frappe.get_doc(
        {
            "doctype": "Pulse Update",
            "repair_request": repair_request,
            "status": status,
            "details": details,
            "percent_complete": percent_complete,
        }
    )
    doc.insert()

    # Scope realtime event to this Repair Request
    frappe.publish_realtime(
        event="repair_portal.pulse_update",
        message=doc.as_dict(),
        doctype="Repair Request",
        docname=repair_request,
    )

    return doc.name
