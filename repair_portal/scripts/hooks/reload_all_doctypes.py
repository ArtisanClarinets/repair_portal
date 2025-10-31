#!/usr/bin/env python3
"""
Relative Path: repair_portal/scripts/hooks/reload_all_doctypes.py

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

# Path to your app’s folder under apps/
APP_PATH = "/home/frappe/frappe-bench/apps/repair_portal/repair_portal"

# Counters
reload_count = 0
count = 0
error_count = 0


def log(message):
    """
    Simple logging function: print to console and write to Frappe’s log.
    """
    print(message)
    frappe.logger().info(message)


def sanitize_item(item):
    """
    Given a dict representing a Workflow or Workflow State,
    convert any list-valued 'only_allow_edit_for' or 'allowed'
    into newline-separated strings.
    Returns True if modifications were made.
    """
    changed = False

    # Fix states
    for state in item.get("states", []):
        if isinstance(state.get("only_allow_edit_for"), list):
            state["only_allow_edit_for"] = "\n".join(state["only_allow_edit_for"])
            changed = True

    # Fix transitions
    for transition in item.get("transitions", []):
        if isinstance(transition.get("allowed"), list):
            transition["allowed"] = "\n".join(transition["allowed"])
            changed = True

    return changed


def sanitize_workflow_json(json_path):
    """
    Load the JSON (which may be a dict or a list), sanitize any workflow
    entries within, and write back if anything changed.
    """
    try:
        with open(json_path, "r") as f:  # noqa: UP015
            data = json.load(f)
    except json.JSONDecodeError as e:
        log(f"⚠️  Could not parse JSON in {json_path}: {e}")
        return

    changed = False

    # If it's a single dict, wrap in list for uniform processing
    if isinstance(data, dict):
        items = [data]
    elif isinstance(data, list):
        items = data
    else:
        log(f"ℹ️  Unexpected JSON root (not dict or list) in {json_path}, skipping.")
        return

    # Sanitize each workflow item
    for item in items:
        if not isinstance(item, dict):
            continue
        # Only process actual Workflow definitions
        if item.get("doctype") in ("Workflow", "Workflow State") and sanitize_item(item):
            changed = True

    # Write back if anything changed
    if changed:
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        log(f"✅ Sanitized workflow file: {json_path}")


def reload_all_doctypes():
    """
    Walk the app directory, find all valid documents, sanitize workflows,
    and reload them using frappe.reload_doc.
    """
    global count, reload_count, error_count

    log("🔄 Reloading all documents in repair_portal...")

    for dirpath, _, filenames in os.walk(APP_PATH): # type: ignore
        for filename in filenames:
            if not filename.endswith(".json"):
                continue

            docname = os.path.basename(dirpath)
            if filename != f"{docname}.json":
                continue

            # Determine doctype_type and module from the path
            parent_dir = os.path.dirname(dirpath)
            doctype_type = os.path.basename(parent_dir)
            relative_to_app = os.path.relpath(parent_dir, APP_PATH) # type: ignore
            module = relative_to_app.split(os.sep)[0]
            json_path = os.path.join(dirpath, filename)

            # Count every attempt
            count += 1

            # Sanitize if this is a Workflow JSON directory
            if doctype_type.lower() == "workflow":
                sanitize_workflow_json(json_path)

            try:
                frappe.logger().info(f"🔹 Reloading: {module} > {doctype_type} > {docname}")
                frappe.reload_doc(module, doctype_type, docname, force=True)
                reload_count += 1
            except Exception as e:
                error_message = f"❌ Error reloading {module}/{doctype_type}/{docname}: {e}"
                frappe.logger().error(error_message)
                log(f"{error_message} 🔹 File Path: {json_path}")
                error_count += 1

    log(f"🔄 Reloaded {reload_count} documents with {error_count} errors.")
    log(f"✅ All {count} reload attempts completed.")


if __name__ == "__main__":
    reload_all_doctypes()
