# File: repair_portal/repair_portal/repair_order/server_script/repair_order_invoice_auto.py
# Updated: 2025-06-26
# Version: 1.0
# Purpose: Automatically create Sales Invoice upon submission of Repair Order

import frappe
from frappe.model.document import Document

def on_submit(doc, method):
    if doc.doctype != "Repair Order":
        return

    invoice = frappe.new_doc("Sales Invoice")
    invoice.customer = doc.customer
    invoice.append("items", {
        "item_code": "REPAIR-SERVICE",
        "qty": 1,
        "rate": 150.00
    })
    invoice.insert(ignore_permissions=True)
    invoice.submit()