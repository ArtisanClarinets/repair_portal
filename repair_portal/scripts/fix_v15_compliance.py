#!/usr/bin/env python3
# Frappe v15 Compliance Fix Script
# Last Updated: 2025-07-19
# Version: v1.0
# Purpose: Fix critical Frappe v15 compliance issues

import glob
import json


def fix_child_table_fields(file_path):
    """Add required parent table fields to child DocTypes."""
    with open(file_path) as f:
        data = json.load(f)

    if data.get("istable") == 1:
        required_fields = ["parent", "parenttype", "parentfield", "idx"]
        existing_fieldnames = [field.get("fieldname") for field in data.get("fields", [])]

        # Add missing required fields
        for field in required_fields:
            if field not in existing_fieldnames:
                if field == "parent":
                    data["fields"].append({"fieldname": "parent", "fieldtype": "Data", "hidden": 1})
                elif field == "parenttype":
                    data["fields"].append({"fieldname": "parenttype", "fieldtype": "Data", "hidden": 1})
                elif field == "parentfield":
                    data["fields"].append({"fieldname": "parentfield", "fieldtype": "Data", "hidden": 1})
                elif field == "idx":
                    data["fields"].append({"fieldname": "idx", "fieldtype": "Int", "hidden": 1})

        # Add engine for v15 compliance
        if "engine" not in data:
            data["engine"] = "InnoDB"

        # Write back
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Fixed child table: {file_path}")


def main():
    """Fix all child table DocTypes."""
    repair_portal_path = "/opt/frappe/erp-bench/apps/repair_portal/repair_portal"

    # Find all DocType JSON files
    pattern = f"{repair_portal_path}/**/doctype/*/*.json"
    doctype_files = glob.glob(pattern, recursive=True)

    fixed_count = 0
    for file_path in doctype_files:
        try:
            with open(file_path) as f:
                data = json.load(f)

            if data.get("doctype") == "DocType" and data.get("istable") == 1:
                fix_child_table_fields(file_path)
                fixed_count += 1

        except Exception as e:
            print(f"⚠️ Error processing {file_path}: {e}")

    print(f"\n🎉 Fixed {fixed_count} child table DocTypes for Frappe v15 compliance!")


if __name__ == "__main__":
    main()
