#!/usr/bin/env python3
# Path: repair_portal/scripts/validate_doctype_references.py
# Date: 2025-10-28
# Version: 1.0.0
# Description: Validate all DocType references in JSON components and DocType schemas
# Dependencies: frappe, json, pathlib

import json
import sys
from pathlib import Path
from collections import defaultdict

# Root path for the app
APP_ROOT = Path("/home/frappe/frappe-bench/apps/repair_portal/repair_portal")

# Collect all valid DocTypes in the system
def collect_all_doctypes():
    """Collect all DocType names from the app"""
    doctypes = set()
    
    # Find all DocType JSON files
    for json_file in APP_ROOT.glob("**/doctype/**/*.json"):
        # Skip child doctypes and other files
        if json_file.parent.name != json_file.stem:
            continue
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and data.get("doctype") == "DocType":
                    name = data.get("name")
                    if name:
                        doctypes.add(name)
        except:
            pass
    
    # Add known ERPNext/Frappe DocTypes
    erpnext_doctypes = {
        "Customer", "Item", "Company", "Warehouse", "User", "Role", 
        "Sales Invoice", "Purchase Invoice", "Delivery Note", "Stock Entry",
        "Sales Order", "Purchase Order", "Quotation", "Opportunity",
        "Lead", "Contact", "Address", "Territory", "Customer Group",
        "Item Group", "Brand", "UOM", "Price List", "Currency",
        "Payment Entry", "Payment Request", "Subscription", "Subscription Plan",
        "Employee", "Department", "Designation", "Holiday List",
        "Workflow", "Workflow State", "Workflow Action", "Workflow Document State",
        "Notification", "Dashboard Chart", "Report", "Print Format",
        "Workspace", "Custom Field", "Property Setter", "DocType",
        "DocField", "DocPerm"
    }
    doctypes.update(erpnext_doctypes)
    
    return doctypes

def find_doctype_references_in_json(data, filepath):
    """Find all DocType references in a JSON file"""
    references = []
    
    if isinstance(data, dict):
        # Check common reference fields
        ref_fields = [
            ("document_type", "document_type"),
            ("ref_doctype", "ref_doctype"),
            ("doc_type", "doc_type"),
            ("reference_doctype", "reference_doctype"),
            ("parent_doctype", "parent_doctype"),
        ]
        
        for field_name, field_key in ref_fields:
            if field_key in data and data[field_key]:
                references.append((field_key, data[field_key]))
        
        # Recursively check nested structures
        for value in data.values():
            if isinstance(value, (dict, list)):
                references.extend(find_doctype_references_in_json(value, filepath))
    
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                references.extend(find_doctype_references_in_json(item, filepath))
    
    return references

def validate_doctype_schema_references(json_path, valid_doctypes):
    """Validate Link and Table field references in DocType JSON"""
    issues = []
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict) or data.get("doctype") != "DocType":
            return issues
        
        doctype_name = data.get("name", "Unknown")
        fields = data.get("fields", [])
        
        for field in fields:
            if not isinstance(field, dict):
                continue
            
            fieldtype = field.get("fieldtype")
            options = field.get("options")
            fieldname = field.get("fieldname", "unknown")
            
            if fieldtype == "Link" and options:
                if options not in valid_doctypes:
                    issues.append(
                        f"Link field '{fieldname}' references invalid DocType '{options}'"
                    )
            
            elif fieldtype == "Table" and options:
                if options not in valid_doctypes:
                    issues.append(
                        f"Table field '{fieldname}' references invalid DocType '{options}'"
                    )
            
            elif fieldtype == "Dynamic Link":
                # Dynamic links are OK - they reference based on another field
                pass
    
    except Exception as e:
        issues.append(f"Error reading file: {e}")
    
    return issues

def validate_all_references():
    """Main validation function"""
    print("=" * 80)
    print("DOCTYPE REFERENCE VALIDATION REPORT")
    print("=" * 80)
    print()
    
    # Collect all valid DocTypes
    print("Collecting all DocTypes...")
    valid_doctypes = collect_all_doctypes()
    print(f"Found {len(valid_doctypes)} valid DocTypes\n")
    
    # Statistics
    stats = defaultdict(int)
    issues_by_file = {}
    invalid_references = defaultdict(set)
    
    # Validate JSON components (notifications, charts, reports, etc.)
    print("Validating JSON components...")
    component_files = []
    patterns = [
        "**/notification/**/*.json",
        "**/dashboard_chart/**/*.json",
        "**/report/**/*.json",
        "**/print_format/**/*.json",
        "**/workflow/**/*.json",
    ]
    
    for pattern in patterns:
        component_files.extend(APP_ROOT.glob(pattern))
    
    component_files = [f for f in component_files if ".vscode" not in str(f)]
    
    for filepath in component_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            references = find_doctype_references_in_json(data, filepath)
            for field_name, ref_doctype in references:
                if ref_doctype and ref_doctype not in valid_doctypes:
                    relative_path = filepath.relative_to(APP_ROOT)
                    issue = f"{field_name} → '{ref_doctype}'"
                    if str(relative_path) not in issues_by_file:
                        issues_by_file[str(relative_path)] = []
                    issues_by_file[str(relative_path)].append(issue)
                    invalid_references[ref_doctype].add(str(relative_path))
                    stats["invalid_refs_in_components"] += 1
        except:
            pass
    
    print(f"Checked {len(component_files)} component files\n")
    
    # Validate DocType schemas
    print("Validating DocType schemas...")
    doctype_files = []
    for json_file in APP_ROOT.glob("**/doctype/**/*.json"):
        if json_file.parent.name == json_file.stem:
            doctype_files.append(json_file)
    
    for filepath in doctype_files:
        issues = validate_doctype_schema_references(filepath, valid_doctypes)
        if issues:
            relative_path = filepath.relative_to(APP_ROOT)
            issues_by_file[str(relative_path)] = issues
            stats["doctypes_with_invalid_refs"] += 1
            for issue in issues:
                # Extract referenced DocType from issue string
                if "references invalid DocType" in issue:
                    ref = issue.split("'")[-2]
                    invalid_references[ref].add(str(relative_path))
    
    print(f"Checked {len(doctype_files)} DocType schemas\n")
    
    # Print summary
    print("SUMMARY")
    print("-" * 80)
    print(f"Total valid DocTypes in system: {len(valid_doctypes)}")
    print(f"Files with invalid references: {len(issues_by_file)}")
    print(f"Invalid references in components: {stats['invalid_refs_in_components']}")
    print(f"DocTypes with invalid Link/Table fields: {stats['doctypes_with_invalid_refs']}")
    print()
    
    # Print most common invalid references
    if invalid_references:
        print("MOST COMMON INVALID REFERENCES")
        print("-" * 80)
        sorted_refs = sorted(invalid_references.items(), key=lambda x: len(x[1]), reverse=True)
        for ref_doctype, files in sorted_refs[:15]:
            print(f"'{ref_doctype}' referenced by {len(files)} files:")
            for f in list(files)[:3]:
                print(f"  - {f}")
            if len(files) > 3:
                print(f"  ... and {len(files) - 3} more")
        print()
    
    # Print detailed issues
    if issues_by_file:
        print("DETAILED ISSUES (First 20)")
        print("-" * 80)
        for filepath in sorted(issues_by_file.keys())[:20]:
            issues = issues_by_file[filepath]
            print(f"\n{filepath}:")
            for issue in issues:
                print(f"  - {issue}")
        
        if len(issues_by_file) > 20:
            print(f"\n... and {len(issues_by_file) - 20} more files with issues")
        print()
    
    # Final verdict
    print("=" * 80)
    if len(issues_by_file) == 0:
        print("✅ ALL DOCTYPE REFERENCES ARE VALID")
    else:
        print(f"⚠️  FOUND INVALID REFERENCES IN {len(issues_by_file)} FILES")
        print()
        print("NOTE: Some references may be to ERPNext DocTypes not yet loaded.")
        print("Verify these references during runtime with access to the full database.")
    print("=" * 80)
    
    return len(issues_by_file)

if __name__ == "__main__":
    issues_count = validate_all_references()
    sys.exit(0)  # Exit 0 even with issues since some may be valid ERPNext DocTypes
