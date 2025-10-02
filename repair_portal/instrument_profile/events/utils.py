# Path: repair_portal/instrument_profile/events/utils.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Event handlers for Instrument Profile lifecycle; auto-creates linked Inspection Report with proper error handling
# Dependencies: frappe

import frappe
from frappe import _


def create_linked_documents(doc, method=None):
    """
    When an Instrument Profile is created, auto-create linked Inspection Report.
    """
    try:
        if frappe.db.exists('Inspection Report', {'instrument_profile': doc.name}):
            return

        inspection = frappe.get_doc(
            {
                'doctype': 'Inspection Report',
                'instrument_profile': doc.name,
                'status': 'Pending',
            }
        )
        inspection.insert(ignore_permissions=True)
        frappe.db.commit()

    except Exception:
        frappe.log_error(frappe.get_traceback(), 'InstrumentProfile Auto-Creation Failed')
