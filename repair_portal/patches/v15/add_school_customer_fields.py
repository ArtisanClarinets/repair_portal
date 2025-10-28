"""Add school account custom fields on Customer."""
from __future__ import annotations

import frappe


CUSTOM_FIELDS = [
    {
        "dt": "Customer",
        "fieldname": "is_school",
        "label": "Is School Account",
        "fieldtype": "Check",
        "insert_after": "customer_type",
        "default": "0",
    },
    {
        "dt": "Customer",
        "fieldname": "district_name",
        "label": "District Name",
        "fieldtype": "Data",
        "insert_after": "is_school",
    },
]


def execute() -> None:
    if not frappe.db.exists("DocType", "Customer"):
        return
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    create_custom_fields({"Customer": [field for field in CUSTOM_FIELDS]})

