# File Header Template
# Relative Path: repair_portal/tools/stock_tools.py
# Last Updated: 2025-07-11
# Version: v1.1
# Purpose: Stock validation utilities like verifying if a serial is Ready for Sale
# Dependencies: Instrument Profile, Item, Bin

import frappe

def verify_ready_for_sale(serial_no: str) -> dict:
    """
    Validate whether a specific serial number is ready for sale.

    Args:
        serial_no (str): The serial number of the instrument to check.

    Returns:
        dict: {'success': True/False, 'reason': str}
    """
    if not serial_no:
        return {"success": False, "reason": "Missing serial number."}

    # PATCH: Ensure serial_no exists as Serial No in ERPNext
    if not frappe.db.exists("Serial No", serial_no):
        return {"success": False, "reason": "Serial No does not exist in ERPNext."}

    profile = frappe.get_all(
        "Instrument Profile",
        filters={"serial_no": serial_no},
        fields=["name", "profile_status", "model"]
    )

    if not profile:
        return {"success": False, "reason": "No Instrument Profile found for that serial."}

    ip = profile[0]
    if ip.profile_status != "Ready":
        return {"success": False, "reason": f"Instrument status is '{ip.profile_status}', not 'Ready'."}

    # Find matching Item by model
    item = frappe.get_all("Item", filters={"item_code": ip.model}, fields=["published"])
    if not item or not item[0].published:
        return {"success": False, "reason": "Item is not published on website."}

    # Check stock exists in any Bin
    qty = frappe.db.get_value("Bin", {"item_code": ip.model}, "actual_qty") or 0
    if qty <= 0:
        return {"success": False, "reason": "No available stock for this instrument."}

    return {"success": True, "reason": "Instrument is Ready for Sale."}