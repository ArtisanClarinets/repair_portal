# repair_portal/repair_portal/patches/remove_duplicate_module_def.py
# Date Updated: 2025-06-16
# Version: 1.0
# Purpose: Remove duplicate Module Def for 'Inspection' to prevent install failure

import frappe


def execute():
    if frappe.db.exists("Module Def", "Inspection"):
        frappe.db.delete("Module Def", {"name": "Inspection"})
        frappe.db.commit()
