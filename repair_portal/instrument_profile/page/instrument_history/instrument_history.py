# File: repair_portal/instrument_profile/page/instrument_history/instrument_history.py
# Updated: 2025-06-14
# Version: 2.0
# Purpose: Full instrument interaction log renderer via serial number

import frappe


@frappe.whitelist()
def get_instrument_history(instrument_id):
    doc = frappe.get_doc("Instrument Profile", instrument_id)

    serial = doc.serial_number

    setups = frappe.get_all(
        "Clarinet Initial Setup",
        fields=["setup_date", "technician", "status"],
        filters={"instrument_profile": instrument_id},
    )
    conditions = frappe.get_all(
        "Instrument Condition Record",
        fields=["date", "technician", "condition_notes"],
        filters={"parent": instrument_id},
    )

    repairs = (
        frappe.get_all(
            "Repair Log", fields=["date", "technician", "repair_notes"], filters={"instrument_serial": serial}
        )
        if frappe.db.exists("DocType", "Repair Log")
        else []
    )
    inspections = (
        frappe.get_all(
            "Inspection Log", fields=["date", "technician", "notes"], filters={"instrument_serial": serial}
        )
        if frappe.db.exists("DocType", "Inspection Log")
        else []
    )
    enhancements = (
        frappe.get_all(
            "Enhancement Log",
            fields=["date", "technician", "description"],
            filters={"instrument_serial": serial},
        )
        if frappe.db.exists("DocType", "Enhancement Log")
        else []
    )

    return {
        "doc": doc,
        "setups": setups,
        "conditions": conditions,
        "repairs": repairs,
        "inspections": inspections,
        "enhancements": enhancements,
    }
