import json
import os
import re
import subprocess
from pathlib import Path

APP_DIR = Path("/opt/frappe/erp-bench/apps/repair_portal/repair_portal")
MODULES_FILE = Path("/opt/frappe/erp-bench/apps/repair_portal/repair_portal/modules.txt")

missing_py_files = []
mismatched_class_names = []
missing_json_files = []
invalid_json_schemas = []
invalid_modules = []
missing_essentials = []
invalid_website_generators = []

with open(MODULES_FILE) as f:
    valid_modules = {line.strip() for line in f if line.strip()}

print("\nPre-Migrate Check Report")
print("==========================")

# Step 1: Lint Python files
print("\nRunning flake8 linting...")
try:
    result = subprocess.run(
        ["flake8", "/opt/frappe/erp-bench/apps/repair_portal/"], capture_output=True, text=True
    )
    if result.returncode != 0 or result.stdout:
        print("❌ Python Linting Issues Found:")

        for line in result.stdout.strip().split("\n"):
            match = re.match(r"(.+):\d+:\d+: F401", line)
            if match:
                file_path = match.group(1)
                with open(file_path) as f:
                    lines = f.readlines()
                with open(file_path, "w") as f:
                    for line_content in lines:
                        if "import frappe" in line_content and "frappe" not in "".join(
                            lines[lines.index(line_content) + 1 :]
                        ):
                            continue
                        f.write(line_content)
    else:
        print("✅ No Python linting issues.")
except Exception as e:
    print(f"⚠️ Failed to run flake8: {e}")

# Step 2: Lint JavaScript files
print("\nRunning ESLint on JS files...")
try:
    eslint_path = "/opt/frappe/erp-bench/apps/repair_portal/eslint.config.js"
    result = subprocess.run(
        ["npx", "eslint", "/opt/frappe/erp-bench/apps/repair_portal/", "--config", eslint_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or result.stdout:
        print("❌ JavaScript Linting Issues Found:")
        print(result.stdout.strip())
        if result.stderr:
            print("[stderr]", result.stderr.strip())
    else:
        print("✅ No JavaScript linting issues.")
except Exception as e:
    print(f"⚠️ Failed to run ESLint: {e}")

# Step 3: Check Doctype JSONs and modules
print("\nChecking Doctype structures and modules...")
for root, _dirs, files in os.walk(APP_DIR):
    if "/report/" in root or "/workspace/" in root:
        continue
    for file in files:
        if file.endswith(".json") and "doctype" in root:
            doctype_path = Path(root)
            doctype_name = doctype_path.name
            py_path = doctype_path / f"{doctype_name}.py"
            json_path = doctype_path / f"{doctype_name}.json"

            if not py_path.exists():
                missing_py_files.append(str(py_path))

            if not json_path.exists():
                missing_json_files.append(str(json_path))
            else:
                try:
                    with open(json_path) as jf:
                        doc = json.load(jf)
                        for field in ["doctype", "name", "module", "fields"]:
                            if field not in doc:
                                invalid_json_schemas.append(str(json_path))
                        if "module" in doc and doc["module"] not in valid_modules:
                            invalid_modules.append(f'{json_path} - invalid module: {doc["module"]}')

                        # Website generator validation
                        if (
                            doc.get("is_published_field")
                            or any(f.get("fieldname") == "route" for f in doc.get("fields", []))
                        ) and py_path.exists():
                            with open(py_path) as f:
                                py_code = f.read()
                            if "WebsiteGenerator" not in py_code:
                                invalid_website_generators.append(
                                    f"{py_path} - missing WebsiteGenerator base class"
                                )
                except Exception as e:
                    invalid_json_schemas.append(f"{str(json_path)} - Error: {e}")

            expected_class_name = "".join(word.capitalize() for word in doctype_name.split("_"))
            if py_path.exists():
                with open(py_path) as f:
                    content = f.read()
                    if f"class {expected_class_name}(Document)" not in content:
                        mismatched_class_names.append((str(py_path), expected_class_name))

# Step 4: Check essential app files
ROOT_APP_DIR = Path("/opt/frappe/erp-bench/apps/repair_portal")
essentials = [
    ROOT_APP_DIR / "setup.py",
    ROOT_APP_DIR / "modules.txt",
    APP_DIR / "hooks.py",
    APP_DIR / "config/desktop.py",
    APP_DIR / "config/__init__.py",
]
for essential in essentials:
    if not essential.exists():
        missing_essentials.append(str(essential))

# Output results
if missing_py_files:
    print("❌ Missing Python Controller Files:")
    for path in missing_py_files:
        print(f" - {path}")
else:
    print("✅ All controller files found.")

if mismatched_class_names:
    print("❌ Mismatched Controller Class Names:")
    for path, expected in mismatched_class_names:
        print(f" - {path}: should define `class {expected}(Document)`")
else:
    print("✅ All controller class names are valid.")

if missing_json_files:
    print("❌ Missing Doctype JSON Files:")
    for path in missing_json_files:
        print(f" - {path}")
else:
    print("✅ All Doctype JSON files found.")

if invalid_json_schemas:
    print("❌ Invalid Doctype JSON Schemas:")
    for path in invalid_json_schemas:
        print(f" - {path}")
else:
    print("✅ All Doctype JSON schemas are valid.")

if invalid_modules:
    print("❌ Invalid Module References in JSONs:")
    for path in invalid_modules:
        print(f" - {path}")
else:
    print("✅ All Doctype modules match modules.txt.")

if missing_essentials:
    print("❌ Missing Essential Files:")
    for path in missing_essentials:
        print(f" - {path}")
else:
    print("✅ All essential configuration files are present.")

if invalid_website_generators:
    print("❌ Missing WebsiteGenerator references in web-published Doctypes:")
    for path in invalid_website_generators:
        print(f" - {path}")
else:
    print("✅ All WebsiteGenerators are properly defined.")

print("\n✔ Use this report before any install or migration.")
