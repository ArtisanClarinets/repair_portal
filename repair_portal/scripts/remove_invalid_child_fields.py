# /opt/frappe/erp-bench/apps/repair_portal/repair_portal/scripts/remove_invalid_child_fields.py
# Updated: 2025-06-16
# Version: 1.2
# Purpose: Recursively clean invalid system fields from child table DocType JSONs

import json
import os

standard_fields = {'parent', 'parenttype', 'parentfield', 'idx'}

def clean_fields(path):
    if not path.endswith('.json') or '/doctype/' not in path:
        return
    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to read {path}: {e}")
        return

    if not isinstance(data, dict) or data.get('doctype') != 'DocType':
        return

    if not data.get('istable'):
        return

    original_len = len(data.get('fields', []))
    data['fields'] = [field for field in data.get('fields', []) if field.get('fieldname') not in standard_fields]
    removed = original_len - len(data['fields'])

    data['istable'] = 1
    data['is_child_table'] = 1

    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Cleaned {removed} fields from {path}")

for root, _dirs, files in os.walk('/opt/frappe/erp-bench/apps/repair_portal/repair_portal'):
    for file in files:
        clean_fields(os.path.join(root, file))