#!/usr/bin/env python3
"""
Reload all doctypes in the app recursively by finding all *.json files
following the structure:
(module)/(doctype)/(docname)/(docname.json)
"""

import os
import json
import frappe

APP_PATH = "/opt/frappe/erp-bench/apps/repair_portal/repair_portal"

def sanitize_workflow_json(json_path):
    """
    Fix 'allowed' and 'only_allow_edit_for' fields if they are lists.
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    changed = False

    # Fix states
    for state in data.get("states", []):
        if isinstance(state.get("only_allow_edit_for"), list):
            state["only_allow_edit_for"] = "\n".join(state["only_allow_edit_for"])
            changed = True

    # Fix transitions
    for transition in data.get("transitions", []):
        if isinstance(transition.get("allowed"), list):
            transition["allowed"] = "\n".join(transition["allowed"])
            changed = True

    if changed:
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Sanitized workflow file: {json_path}")

def reload_all_doctypes():
    """
    Walk the app directory, sanitize workflow files, and reload everything.
    """
    print("🔄 Reloading all doctypes in repair_portal...")

    for dirpath, dirnames, filenames in os.walk(APP_PATH):
        for filename in filenames:
            if filename.endswith(".json"):
                # Check if it matches the desired pattern
                relative_path = os.path.relpath(os.path.join(dirpath, filename), APP_PATH)
                parts = relative_path.split(os.sep)

                if len(parts) == 4:
                    module = parts[0]
                    doctype = parts[1]
                    docname = parts[2]
                    json_path = os.path.join(dirpath, filename)

                    # Confirm the file is named correctly (docname.json)
                    if filename == f"{docname}.json":
                        # Sanitize workflows if applicable
                        if doctype == "workflow":
                            sanitize_workflow_json(json_path)

                        try:
                        #    print(f"🔹 Reloading module='{module}' doctype='{doctype}' docname='{docname}'")
                            frappe.reload_doc(module, doctype, docname)
                        except Exception as e:
                            frappe.logger().error(f"❌ Failed reloading {module}/{doctype}/{docname}: {e}")
                            print(f"❌ Failed reloading {module}/{doctype}/{docname}: {e}")

    print("✅ All reload attempts completed.")
