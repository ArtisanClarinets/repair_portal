import frappe

def run():
    for name in frappe.get_all("Workspace", filters={"module": "Repair Portal"}):
        frappe.delete_doc("Workspace", name.name, force=1)
    frappe.db.commit()