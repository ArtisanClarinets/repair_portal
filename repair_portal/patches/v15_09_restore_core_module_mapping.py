import frappe


def execute():
    if not frappe.db.table_exists("Module Def"):
        return

    if not frappe.db.exists("Module Def", "Core"):
        return

    current_app = frappe.db.get_value("Module Def", "Core", "app_name")
    if current_app != "repair_portal":
        return

    frappe.db.set_value("Module Def", "Core", "app_name", "frappe")
    frappe.db.set_value("Module Def", "Core", "custom", 0)
