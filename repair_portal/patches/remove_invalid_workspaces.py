# Path: repair_portal/patches/remove_invalid_workspaces.py
# Updated: 2025-06-11
# Version: 0.0.1
# Purpose: Remove Workspace records with raw list content and reload valid workspace files.

import json

import frappe


def execute():
    # Remove bad Workspace entries where content is a list instead of a JSON string
    raw_list_workspaces = frappe.get_all('Workspace', filters={}, fields=['name', 'content'])
    for ws in raw_list_workspaces:
        try:
            content = json.loads(ws.content)
            if isinstance(content, list):
                frappe.delete_doc('Workspace', ws.name)
        except Exception:
            continue

    frappe.db.commit()
    frappe.clear_cache()
    print('✅ Removed workspace records with invalid content structure.')
