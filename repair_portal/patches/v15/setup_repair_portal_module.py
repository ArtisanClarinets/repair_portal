"""Ensure Repair Portal module, core roles, and naming series exist."""
from __future__ import annotations

import frappe
from frappe.model.document import Document

MODULE_NAME = "Repair Portal"
ROLE_NAMES = [
    "Owner/Admin",
    "Front Desk",
    "Repair Technician",
    "Inventory",
    "Ecommerce/Marketing",
    "Accounting",
    "School/Teacher",
    "Customer",
    "Intake Coordinator",
]
SERIES_PATTERNS = {
    "Instrument": "INS-.YYYY.-.#####",
    "Player Profile": "PLYR-.YYYY.-.#####",
    "Clarinet Intake": "INTK-.YYYY.-.#####",
    "Repair Request": "REP-REQ-.YYYY.-.#####",
    "Repair Order": "REP-ORD-.YYYY.-.#####",
    "Repair Estimate": "REP-EST-.YYYY.-.#####",
    "Repair Class Template": "RCL-TEMP-.#####",
    "Mail-In Repair Request": "MAIL-REP-.YYYY.-.#####",
    "Technician Availability": "TECH-AVAIL-.YYYY.-.#####",
    "Clarinet BOM Template": "CL-BOM-.#####",
    "Vendor Turnaround Log": "VEND-TURN-.#####",
    "Service Plan": "SRV-PLAN-.#####",
    "Service Plan Enrollment": "SRV-ENR-.YYYY.-.#####",
    "Rental Contract": "RENT-.YYYY.-.#####",
    "Warranty Claim": "WARR-CLM-.YYYY.-.#####",
    "QA Checklist": "QA-CHK-.YYYY.-.#####",
}


def execute() -> None:
    """Idempotent setup for module metadata and numbering."""
    ensure_module()
    ensure_roles()
    ensure_naming_series()


def ensure_module() -> None:
    if frappe.db.exists("Module Def", MODULE_NAME):
        return
    module_doc = frappe.get_doc({
        "doctype": "Module Def",
        "module_name": MODULE_NAME,
        "app_name": "repair_portal",
    })
    module_doc.insert(ignore_permissions=True)


def ensure_roles() -> None:
    for role in ROLE_NAMES:
        if frappe.db.exists("Role", role):
            continue
        role_doc: Document = frappe.get_doc({"doctype": "Role", "role_name": role})
        role_doc.insert(ignore_permissions=True)


def ensure_naming_series() -> None:
    for doctype, pattern in SERIES_PATTERNS.items():
        prefix = pattern.split("#", 1)[0].strip()
        if prefix and not frappe.db.exists("Series", prefix):
            frappe.get_doc({"doctype": "Series", "name": prefix, "current": 0}).insert(
                ignore_permissions=True
            )
        try:
            meta = frappe.get_meta(doctype, cached=False)
        except frappe.DoesNotExistError:
            continue
        field = meta.get_field("naming_series")
        if field and field.default != pattern:
            frappe.db.set_value(
                "DocField",
                {"parent": doctype, "fieldname": "naming_series"},
                "default",
                pattern,
            )

