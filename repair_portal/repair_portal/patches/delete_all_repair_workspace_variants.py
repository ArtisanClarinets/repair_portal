import frappe

def execute():
    for name in ["Repair Portal", "repair-portal"]:
        if frappe.db.exists("Workspace", name):
            frappe.delete_doc("Workspace", name, force=True)

    for ws in frappe.get_all("Workspace", filters={"title": "Repair Portal"}):
        frappe.delete_doc("Workspace", ws.name, force=True)

    frappe.db.commit()