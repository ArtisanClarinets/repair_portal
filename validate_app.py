import os
import frappe
from collections import defaultdict

# --- CONFIGURATION ---
# The name of your custom app as it appears in the 'apps' directory.
APP_NAME = "repair_portal"
# --- END CONFIGURATION ---

# The full path to your app.
app_path = os.path.join(frappe.get_bench_path(), "apps", APP_NAME)

# Dictionary to hold cumulative permission counts.
# Format: { 'Role Name': { 'permission_type': count } }
cumulative_permissions = defaultdict(lambda: defaultdict(int))

# List of all standard permission types in Frappe.
PERM_TYPES = [
    "read", "write", "create", "delete", "submit", "cancel",
    "amend", "report", "import", "export", "print", "email", "share"
]

def run_validation():
    """Main function to run all validation checks and print reports."""
    print("---" * 20)
    print(f"🔍 Starting validation for app: '{APP_NAME}'")
    print(f"📍 App Path: {app_path}")
    print("---" * 20)

    # Run all checks
    check_file_system()
    check_for_debug_statements()
    process_doctype_permissions()

    # Print the final reports
    print_permissions_report()

    print("\n✅ Validation script finished.")
    print("---" * 20)


def check_file_system():
    """Checks for the existence of essential files and directories."""
    print("\n## 📂 File System & Structure Checks\n")
    
    required_files = [
        "setup.py",
        os.path.join(APP_NAME, "hooks.py"),
        os.path.join(APP_NAME, "__init__.py")
    ]
    
    all_found = True
    for file_path in required_files:
        full_path = os.path.join(app_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing essential file: {file_path}")
            all_found = False
            
    if all_found:
        print("\n✨ Basic file structure looks good.")
    else:
        print("\n⚠️  Your app is missing one or more critical files.")


def check_for_debug_statements():
    """Scans .py and .js files for common debug statements."""
    print("\n## 🐛 Debug Statement Checks\n")
    
    py_debug_terms = ["import pdb", "print("]
    js_debug_terms = ["console.log", "debugger"]
    found_issues = []

    for root, _, files in os.walk(app_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f):
                        if any(term in line for term in py_debug_terms) and not line.strip().startswith('#'):
                            found_issues.append(f"   - Python Debug: Found in '{file_path}' on line {i+1}")
            
            elif file.endswith(".js"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f):
                        if any(term in line for term in js_debug_terms) and not line.strip().startswith('//'):
                           found_issues.append(f"   - JS Debug: Found in '{file_path}' on line {i+1}")

    if not found_issues:
        print("✨ No common debug statements found. Good to go!")
    else:
        print("⚠️  Found potential debug statements left in the code:")
        for issue in found_issues:
            print(issue)


def process_doctype_permissions():
    """Fetches and processes permissions for all DocTypes in the app."""
    print("\n## 🔐 Processing App Permissions...\n")
    
    # Get all DocTypes that belong to this app's module.
    app_doctypes = frappe.get_all("DocType", filters={"module": APP_NAME}, pluck="name")

    if not app_doctypes:
        print(f"No DocTypes found for module '{APP_NAME}'. Skipping permissions check.")
        return

    print(f"Found {len(app_doctypes)} DocType(s) in this app. Analyzing permissions...")

    # Fetch all permission rules for these DocTypes.
    docperms = frappe.get_all(
        "DocPerm",
        filters={"parent": ("in", app_doctypes)},
        fields=["parent", "role"] + PERM_TYPES
    )

    for perm in docperms:
        role = perm.get("role")
        for ptype in PERM_TYPES:
            # If the permission is checked (value is 1), increment the count.
            if perm.get(ptype):
                cumulative_permissions[role][ptype] += 1


def print_permissions_report():
    """Prints the final cumulative permissions report to the console."""
    print("\n---" * 20)
    print("## 📊 Cumulative Permissions Report")
    print("---" * 20)

    if not cumulative_permissions:
        print("No custom permissions were found for the DocTypes in this app.")
        return

    # Sort roles for consistent output
    sorted_roles = sorted(cumulative_permissions.keys())

    for role in sorted_roles:
        perms = cumulative_permissions[role]
        
        # Build the inline list of permissions for the current role.
        perm_strings = []
        for ptype in PERM_TYPES:
            count = perms.get(ptype, 0)
            if count > 0:
                perm_strings.append(f"{ptype.capitalize()}: {count}")
        
        print(f"👤 **{role}**")
        print(f"   - " + ", ".join(perm_strings))
        print("-" * 10)


# --- Script Entry Point ---
if __name__ == "__main__":
    # This check ensures the code runs only when executed as a script.
    # The 'frappe.init' is necessary to connect to the site's database.
    try:
        frappe.init(site="erp.artisanclarinets.com") # IMPORTANT: Change this!
        frappe.connect()
        run_validation()
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Ensure you have set the correct site name in the script and are running it via `bench execute`.")
    finally:
        frappe.destroy()

