# Relative Path: repair_portal/api/clarinet_utils.py
# Last Updated: 2025-07-03
# Version: 1.0
# Purpose: Utility functions for clarinet-related operations.
# Notes: Adds proper error handling and docstrings.

import frappe


def get_instrument_profile(serial_no):
    """
    Fetch Instrument Profile by serial number.
    Raises if not found.
    """
    profile = frappe.db.get_value(
        "Instrument Profile",
        {"serial_no": serial_no},
        ["name", "instrument_type", "status"],  # type: ignore
        as_dict=True,
    )
    if not profile:
        frappe.throw(f"No Instrument Profile found for serial number '{serial_no}'")
    return profile


def mark_instrument_archived(instrument_name):
    """
    Marks an Instrument Profile as archived.
    """
    if not frappe.db.exists("Instrument Profile", instrument_name):
        frappe.throw(f"Instrument Profile '{instrument_name}' does not exist.")

    frappe.db.set_value("Instrument Profile", instrument_name, "status", "Archived")
