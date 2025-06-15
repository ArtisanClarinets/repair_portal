import frappe


def execute():
    workspace_names = [
        ("repair-tools-workspace", "Tools"),
        ("repair-enhancements-workspace", "Enhancements"),
    ]

    for name, label in workspace_names:
        if not frappe.db.exists("Workspace", name):
            frappe.get_doc(
                {
                    "doctype": "Workspace",
                    "name": name,
                    "label": label,
                    "title": label,
                    "module": "Repair Portal",
                    "is_standard": 1,
                    "public": 1,
                    "content": "[]",
                }
            ).insert(ignore_permissions=True)

    frappe.db.commit()
