import os, json

base = "/opt/frappe/erp-bench/apps/repair_portal/repair_portal"

for root, dirs, files in os.walk(base):
    for file in files:
        if file.endswith(".json"):
            full_path = os.path.join(root, file)
            try:
                with open(full_path) as f:
                    doc = json.load(f)
                for key, value in doc.items():
                    if isinstance(value, list):
                        for idx, entry in enumerate(value):
                            if isinstance(entry, str):
                                print(f"❌ {full_path} → entry {idx} in {key} is str not dict")
                    if key == "fields" and isinstance(value, str):
                        print(f"❌ {full_path} → fields key is str")
            except Exception as e:
                print(f"⚠️ {full_path} → Error: {e}")