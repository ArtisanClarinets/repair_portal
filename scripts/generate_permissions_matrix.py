import json
import os
from pathlib import Path

ROLES = [
    {"role": "Technician", "read": 1, "write": 1, "create": 1},
    {"role": "Workshop Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "delete": 1},
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "delete": 1, "amend": 1, "export": 1, "import": 1}
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