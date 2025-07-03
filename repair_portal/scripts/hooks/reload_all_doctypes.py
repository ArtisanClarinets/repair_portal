#!/usr/bin/env python3
"""
Reloads all documents in the 'repair_portal' app by recursively finding 
all *.json files that follow the standard Frappe structure:
.../doctype_type/docname/docname.json

This script should be run within the Frappe bench context.
Example:
bench --site your_site_name execute /path/to/this/script.py
"""

import json
import os

import frappe

APP_PATH = "/opt/frappe/erp-bench/apps/repair_portal/repair_portal"
reload_count = 0
count = 0
error_count = 0


def log(message):
    """
    Simple logging function to print messages.
    """
    log(message)
    frappe.logger().info(message)


def sanitize_workflow_json(json_path):
    """
    Fix 'allowed' and 'only_allow_edit_for' fields in workflow JSON
    if they are incorrectly formatted as lists instead of string.
    """
    try:
        with open(json_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"⚠️  Could not parse JSON in {json_path}: {e}")
        return

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
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")  # Add trailing newline
        print(f"✅ Sanitized workflow file: {json_path}")


def reload_all_doctypes():
    """
    Walk the app directory, find all valid documents, sanitize workflows,
    and reload them using frappe.reload_doc.
    """
    global count, reload_count, error_count
    print("🔄 Reloading all documents in repair_portal...")

    for dirpath, _, filenames in os.walk(APP_PATH):
        for filename in filenames:
            if not filename.endswith(".json"):
                continue

            # Robust check: A reloadable document's JSON file name
            # must match its parent directory's name.
            docname = os.path.basename(dirpath)
            if filename == f"{docname}.json":

                # Get the doctype_type (e.g., 'DocType', 'Report', 'Workflow')
                # and the module.
                parent_dir = os.path.dirname(dirpath)
                doctype_type = os.path.basename(parent_dir)

                # We can get the module from the relative path
                relative_to_app = os.path.relpath(parent_dir, APP_PATH)
                module = relative_to_app.split(os.sep)[0]

                json_path = os.path.join(dirpath, filename)

                # Sanitize workflows if applicable
                if doctype_type == "workflow":
                    sanitize_workflow_json(json_path)

                try:
                    frappe.logger().info(f"🔹 Reloading: {module} > {doctype_type} > {docname}")
                    frappe.reload_doc(module, doctype_type, docname, force=True)
                    reload_count += 1
                except Exception as e:
                    error_message = f"❌ Error: {e} 🔹 File Path: {json_path}"
                    frappe.logger().error(f" Failed reloading {module}/{doctype_type}/{docname}: {e}")
                    frappe.logger().error(error_message)
                    error_count += 1
                    print(f"{error_message} 🔹  ⚠️ File Path: {json_path}")

    print(f"🔄 Reloaded {reload_count} documents with {error_count} errors.")
    print(f"✅ All {count} reload attempts completed.")


# To run the script
if __name__ == "__main__":
    reload_all_doctypes()
