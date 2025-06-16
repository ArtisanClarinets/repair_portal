# /opt/frappe/erp-bench/apps/repair_portal/repair_portal/scripts/fix_istable_fields.py
# Date Updated: 2025-06-16
# Version: 1.0
# Purpose: Automatically patch all istable=1 DocTypes to include required table fields.

import os
import json

DOC_ROOT = "/opt/frappe/erp-bench/apps/repair_portal/repair_portal"
REQUIRED_FIELDS = ["parent", "parenttype", "parentfield", "idx"]

def patch_istable_doctypes():
    for root, dirs, files in os.walk(DOC_ROOT):
        for file in files:
            if file.endswith(".json") and os.path.exists(os.path.join(root, file)):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r') as f:
                        data = json.load(f)

                    if data.get("istable") == 1:
                        existing_fields = {f.get("fieldname") for f in data.get("fields", []) if "fieldname" in f}
                        needs_update = any(field not in existing_fields for field in REQUIRED_FIELDS)

                        if needs_update:
                            for field in REQUIRED_FIELDS:
                                if field not in existing_fields:
                                    field_def = {
                                        "fieldname": field,
                                        "label": field.title(),
                                        "fieldtype": "Data" if field != "idx" else "Int",
                                        "read_only": 1,
                                        "in_list_view": 0,
                                        "in_standard_filter": 0,
                                        "hidden": 1
                                    }
                                    data["fields"].append(field_def)

                            with open(full_path, 'w') as f:
                                json.dump(data, f, indent=2)
                            print(f"✅ Patched: {full_path}")

                except Exception as e:
                    print(f"❌ Error in {full_path}: {str(e)}")

if __name__ == '__main__':
    patch_istable_doctypes()