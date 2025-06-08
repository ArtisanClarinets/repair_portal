import frappe

def execute():
    # Delete both old conflicting entries
    for name in ["Repair Portal", "repair-portal"]:
        if frappe.db.exists("Workspace", name):
            frappe.delete_doc("Workspace", name, force=True)
            frappe.db.commit()