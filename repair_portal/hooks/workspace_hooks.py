# repair_portal/hooks/workspace_hooks.py
# Updated: 2025-06-10
# Version: 1.1
# Purpose: Hook logic to auto-generate and update workspaces after migrate

import frappe


def generate_workspaces():
    try:
        # Run workspace generator
        from repair_portal.command import workspace_gen

        workspace_gen.generate_all()

        # Run module scanner updater
        from repair_portal.command import module_scanner

        module_scanner.scan_modules_and_update()

        print("✅ Workspaces generated and updated with module contents.")

    except Exception as e:
        frappe.log_error(title="Workspace Generation Error", message=str(e))
        print(f"❌ Error during workspace generation: {e}")
