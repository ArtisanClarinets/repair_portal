import json
import os
from pathlib import Path

ROLES = [
    {"role": "Technician", "read": 1, "write": 1, "create": 1},
    {
        "role": "Workshop Manager",
        "read": 1,
        "write": 1,
        "create": 1,
        "submit": 1,
        "cancel": 1,
        "delete": 1,
    },
    {
        "role": "System Manager",
        "read": 1,
        "write": 1,
        "create": 1,
        "submit": 1,
        "cancel": 1,
        "delete": 1,
        "amend": 1,
        "export": 1,
        "import": 1,
    },
    {
        "role": "Administrator",
        "read": 1,
        "write": 1,
        "create": 1,
        "submit": 1,
        "cancel": 1,
        "delete": 1,
        "amend": 1,
        "export": 1,
        "import": 1,
    },
    {
        "role": "Guest",
        "read": 1,
        "write": 0,
        "create": 0,
        "submit": 0,
        "cancel": 0,
        "delete": 0,
        "amend": 0,
        "export": 0,
        "import": 0,
    },
    {
        "role": "Supplier",
        "read": 1,
        "write": 1,
        "create": 1,
        "submit": 1,
        "cancel": 1,
        "delete": 0,
        "amend": 0,
        "export": 0,
        "import": 0,
    },
    {"role": "Maintenance Staff", "read": 1, "write": 1, "create": 1},
    {"role": "Inventory Manager", "read": 1, "write": 1, "create": 1},
    {
        "role": "Quality Control",
        "read": 1,
        "write": 0,
        "create": 0,
        "submit": 0,
        "cancel": 0,
        "delete": 0,
        "amend": 0,
        "export": 0,
        "import": 0,
    },
    {
        "role": "Finance",
        "read": 1,
        "write": 1,
        "create": 1,
        "submit": 1,
        "cancel": 1,
        "delete": 0,
        "amend": 0,
        "export": 1,
        "import": 0,
    },
    {"role": "Logistics", "read": 1, "write": 1, "create": 1},
    {"role": "IT Support", "read": 1, "write": 1, "create": 1},
    {
        "role": "External Auditor",
        "read": 1,
        "write": 0,
        "create": 0,
        "submit": 0,
        "cancel": 0,
        "delete": 0,
        "amend": 0,
        "export": 1,
        "import": 0,
    },
    {
        "role": "Compliance Officer",
        "read": 1,
        "write": 0,
        "create": 0,
        "submit": 0,
        "cancel": 0,
        "delete": 0,
        "amend": 0,
        "export": 1,
        "import": 0,
    },
]

APP_ROOT = Path(__file__).resolve().parent.parent / "repair_portal/repair_portal"


def update_permissions(json_path):
    with open(json_path) as f:
        data = json.load(f)

    data["permissions"] = ROLES

    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Patched permissions: {json_path}")


for root, dirs, files in os.walk(APP_ROOT):
    for file in files:
        if file.endswith(".json") and "doctype" in root:
            update_permissions(Path(root) / file)
