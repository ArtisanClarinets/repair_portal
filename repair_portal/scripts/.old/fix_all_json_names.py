#!/usr/bin/env python3
"""
Script to format the "name" key in all JSON files recursively.
- Replaces underscores and hyphens with spaces
- Title-cases each word

Usage:
bench --site erp.artisanclarinets.com execute repair_portal.scripts.fix_all_json_names.fix_all_json_names
"""

import json
import os

APP_PATH = "/opt/frappe/erp-bench/apps/repair_portal/repair_portal"


def fix_all_json_names():
    """
    Traverse the app and update 'name' in all JSON files to be clean.
    """
    print("🔄 Validating and fixing all JSON 'name' keys...")

    fixed_count = 0
    skipped_count = 0
    error_count = 0

    for dirpath, dirnames, filenames in os.walk(APP_PATH):
        for filename in filenames:
            if filename.endswith(".json"):
                json_path = os.path.join(dirpath, filename)
                relative_path = os.path.relpath(json_path, APP_PATH)

                try:
                    with open(json_path) as f:
                        data = json.load(f)

                    # Skip files that are not dicts
                    if not isinstance(data, dict):
                        skipped_count += 1
                        continue

                    original_name = data.get("name")
                    if not original_name:
                        skipped_count += 1
                        continue

                    # Clean up the name
                    cleaned_name = original_name.replace("-", " ").replace("_", " ").lower().split()
                    formatted_name = " ".join(word.capitalize() for word in cleaned_name)

                    if formatted_name != original_name:
                        data["name"] = formatted_name
                        with open(json_path, "w") as f:
                            json.dump(data, f, indent=2)
                        print(f"✅ Fixed 'name' in {relative_path}: '{original_name}' -> '{formatted_name}'")
                        fixed_count += 1
                    else:
                        skipped_count += 1

                except Exception as e:
                    print(f"❌ Error processing {relative_path}: {e}")
                    error_count += 1

    print(f"✅ Complete: {fixed_count} fixed, {skipped_count} unchanged, {error_count} errors.")
