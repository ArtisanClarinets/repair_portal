# ---------------------------------------------------------------------------
# File: repair_portal/instrument_profile/events/utils.py
# Date Updated: 2025-07-02
# Version: v1.0
# Purpose: Auto-create linked documents when Instrument Profile created.
# ---------------------------------------------------------------------------

import frappe


def create_linked_documents(doc, method=None):
    """
    When an Instrument Profile is created, auto-create linked Inspection Report.
    """
    try:
        if frappe.db.exists("Inspection Report", {"instrument_profile": doc.name}):
            return

        inspection = frappe.get_doc(
            {
                "doctype": "Inspection Report",
                "instrument_profile": doc.name,
                "status": "Pending",
            }
        )
        inspection.insert(ignore_permissions=True)
        frappe.db.commit()

    except Exception:
        frappe.log_error(frappe.get_traceback(), "InstrumentProfile Auto-Creation Failed")
