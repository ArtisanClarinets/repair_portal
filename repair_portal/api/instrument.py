"""repair_portal/api/instrument.py
Updated: 2025-08-30
Version: 1.0
Purpose: Expose instrument utilities via REST.
Dev notes: Will be registered as /api/method/repair_portal.api.instrument.*
"""

from __future__ import annotations

import frappe


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def add_service_note(instrument: str, note: str) -> str:
    """Attach a service note to the given instrument."""
    doc = frappe.get_doc("Instrument Profile", instrument)
    doc.append("service_notes", {"note": note})
    doc.save()
    frappe.publish_realtime("service_note_added", {"instrument": instrument})
    return frappe.safe_json.dumps({"status": "ok"})


@frappe.whitelist(allow_guest=False)
@frappe.only_for(["Technician"])
def get_service_history(instrument: str) -> str:
    """Return serialized service history for the instrument."""
    logs = frappe.get_all(
        "Repair Status Update",
        filters={"instrument": instrument},
        fields=["repair_type", "modified"],
        order_by="modified desc",
    )
    return frappe.safe_json.dumps(logs)
