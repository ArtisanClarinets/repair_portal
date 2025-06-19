from __future__ import annotations

import frappe
from frappe.model.document import Document


class PulseUpdate(Document):
    pass


@frappe.whitelist(allow_guest=False, methods=["POST"])
def create_update(repair_request: str, status: str | None = None, details: str | None = None, percent_complete: int | None = None):
    """Create a new Pulse Update and notify viewers in real time."""
    frappe.only_for("Technician")

    doc = frappe.get_doc({
        "doctype": "Pulse Update",
        "repair_request": repair_request,
        "status": status,
        "details": details,
        "percent_complete": percent_complete,
    })
    doc.insert()

    frappe.publish_realtime(f"repair_pulse_{repair_request}", doc.as_dict())
    return doc.name
