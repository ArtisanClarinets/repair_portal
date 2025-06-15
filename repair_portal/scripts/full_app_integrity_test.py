import os
import sys
import importlib
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent / "repair_portal/repair_portal"
failures = []


def validate_doctype_controller(path):
    if not path.name.endswith(".json"):
        return

    module = path.parent
    doctype_name = module.name
    expected_class_name = "".join(p.capitalize() for p in doctype_name.split("_"))
    py_file = module / f"{doctype_name}.py"

    if not py_file.exists():
        failures.append(f"❌ Missing .py controller: {py_file}")
        return

    try:
        rel_module_path = str(module.relative_to(APP_ROOT.parent)).replace(os.sep, ".")
        imported = importlib.import_module(f"repair_portal.{rel_module_path}.{doctype_name}")
        if not hasattr(imported, expected_class_name):
            failures.append(f"❌ Class mismatch in {py_file}: missing `{expected_class_name}`")
    except Exception as e:
        failures.append(f"❌ Import error for {doctype_name}: {str(e)}")


print("🔍 Running Full App Integrity Test...")

for root, dirs, files in os.walk(APP_ROOT):
    for file in files:
        if file.endswith(".json") and "doctype" in root:
            validate_doctype_controller(Path(root) / file)

print("\nIntegrity Report")
print("================")

if failures:
    for f in failures:
        print(f)
    sys.exit(1)
else:
    print("✅ All Doctypes and Controllers are valid.")
