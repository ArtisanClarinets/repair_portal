import frappe

def after_install():
    # Example: Ensure default Repair Service Categories exist
    if not frappe.db.exists("Repair Service Category", {"category_name": "General"}):
        frappe.get_doc({
            "doctype": "Repair Service Category",
            "category_name": "General",
            "description": "General purpose repairs"
        }).insert(ignore_permissions=True)

    # Ensure Workspace is correctly linked
    if not frappe.db.exists("Workspace", "Repair Portal"):
        frappe.get_doc({
            "doctype": "Workspace",
            "label": "Repair Portal",
            "module": "Repair Portal",
            "category": "Modules",
            "data": [],
            "icon": "octicon octicon-tools",
            "is_standard": 1
        }).insert(ignore_permissions=True)