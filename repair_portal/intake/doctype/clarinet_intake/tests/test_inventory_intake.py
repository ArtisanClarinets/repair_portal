import frappe


def test_inventory_intake_creates_children():
    doc = frappe.get_doc(
        {
            "doctype": "Clarinet Intake",
            "intake_type": "Inventory",
            "item_code": "_Test Item",
            "warehouse": "_Test Warehouse - _TC",
        }
    )
    doc.insert()
    assert frappe.db.exists("Instrument Inspection", {"clarinet_intake": doc.name})
    assert frappe.db.exists("Clarinet Initial Setup", {"clarinet_intake": doc.name})
    assert doc.serial_no
