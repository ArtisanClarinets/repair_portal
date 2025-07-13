#!/usr/bin/env python
import frappe
from frappe.model.document import new_doc

def create_stock_receipt(item_code, serial_no, warehouse, qty: int = 1, qc_required: int = 1):
    se = frappe.new_doc("Stock Entry")
    se.stock_entry_type = "Material Receipt"
    se.append("items", {
        "item_code": item_code,
        "serial_no": serial_no,
        "t_warehouse": warehouse,
        "qty": qty,
        "qc_required": qc_required,
    })
    se.insert()
    se.submit()
    return se.name
