# File: repair_portal/service_planning/utils.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Custom utility functions for service planning module

import frappe
from frappe.utils import date_diff, today


def get_warranty_days_left():
    instruments = frappe.db.get_all("Instrument", fields=["name", "warranty_expiry"])
    output = []
    for inst in instruments:
        if inst.get("warranty_expiry"):
            days_left = date_diff(inst.warranty_expiry, today())
            output.append({"name": inst.name, "value": max(days_left, 0)})
    return [{"value": min(i["value"] for i in output) if output else 0}]