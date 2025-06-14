# Report: Loaner Return Flags
# Module: Intake
# Updated: 2025-06-12

import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "linked_loaner", "label": "Loaner Ref", "fieldtype": "Link", "options": "Loaner Instrument", "width": 160},
        {"fieldname": "damage_found", "label": "Damage?", "fieldtype": "Check", "width": 100},
        {"fieldname": "condition_notes", "label": "Condition Notes", "fieldtype": "Text", "width": 300},
        {"fieldname": "return_date", "label": "Return Date", "fieldtype": "Date", "width": 120}
    ]

    data = frappe.get_all(
        "Loaner Return Check",
        fields=["linked_loaner", "damage_found", "condition_notes", "return_date"],
        order_by="return_date desc"
    )

    return columns, data