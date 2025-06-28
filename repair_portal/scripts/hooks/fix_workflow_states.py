#!/usr/bin/env python3
"""
Script to validate and fix all Workflow State JSON files in the app.

Usage:
bench --site erp.artisanclarinets.com execute repair_portal.scripts.fix_workflow_states.fix_workflow_states
"""

import os
import json

APP_PATH = "/opt/frappe/erp-bench/apps/repair_portal/repair_portal"

def fix_workflow_states():
    """
    Traverse the app, validate and auto-correct workflow_state JSON files.
    """
    print("🔄 Validating and fixing Workflow State JSON files...")

    fixed_count = 0
    skipped_count = 0

    for dirpath, dirnames, filenames in os.walk(APP_PATH):
        for filename in filenames:
            if filename.endswith(".json"):
                relative_path = os.path.relpath(os.path.join(dirpath, filename), APP_PATH)
                parts = relative_path.split(os.sep)

                # Match: (module)/workflow_state/(state)/(state).json
                if len(parts) == 4 and parts[1] == "workflow_state":
                    module = parts[0]
                    state = parts[2]

                    json_path = os.path.join(dirpath, filename)

                    with open(json_path, "r") as f:
                        data = json.load(f)

                    changed = False

                    # Enforce doctype
                    if data.get("doctype") != "Workflow State":
                        data["doctype"] = "Workflow State"
                        changed = True


                    # Enforce module
                    if data.get("module") != module.replace("_", " ").title():
                        # Convert e.g., client_profile -> Client Profile
                        data["module"] = module.replace("_", " ").title()
                        changed = True

                    # Enforce is_standard
                    if data.get("is_standard") != 1:
                        data["is_standard"] = 1
                        changed = True

                    # Enforce sync_on_migrate
                    if data.get("sync_on_migrate") != 1:
                        data["sync_on_migrate"] = 1
                        changed = True

                    # Capitalize style
                    style = data.get("style", "")
                    if style and style[0].islower():
                        fixed_style = style.capitalize()
                        if fixed_style != style:
                            data["style"] = fixed_style
                            changed = True

                    if changed:
                        with open(json_path, "w") as f:
                            json.dump(data, f, indent=2)
                        print(f"✅ Fixed: {relative_path}")
                        fixed_count += 1
                    else:
                        skipped_count += 1

    print(f"✅ Completed. Fixed {fixed_count} file(s), skipped {skipped_count} already correct.")
