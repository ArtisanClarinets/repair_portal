#!/usr/bin/env python3
# Path: repair_portal/scripts/audit_json_schemas.py
# Date: 2025-10-28
# Version: 1.0.0
# Description: Comprehensive audit of all JSON schema files in repair_portal app
# Dependencies: frappe, json, pathlib

import json
import sys
from pathlib import Path
from collections import defaultdict

# Root path for the app
APP_ROOT = Path("/home/frappe/frappe-bench/apps/repair_portal/repair_portal")

# Expected doctype fields for each component type
EXPECTED_DOCTYPE_FIELDS = {
    "Notification": "doctype",
    "Dashboard Chart": "doctype",
    "Report": "doctype",
    "Print Format": "doctype",
    "Workflow": "doctype",
    "Workspace": "doctype",
    "Workflow Document State": "doctype",
    "Workflow Action Master": "doctype",
}

# Fields that reference other DocTypes
DOCTYPE_REFERENCE_FIELDS = [
    "document_type",
    "ref_doctype",
    "doc_type",
    "reference_doctype",
    "parent_doctype",
    "options",  # for Link fields in DocTypes
]

def find_all_json_components():
    """Find all JSON component files (notifications, charts, reports, etc.)"""
    patterns = [
        "**/notification/**/*.json",
        "**/dashboard_chart/**/*.json",
        "**/report/**/*.json",
        "**/print_format/**/*.json",
        "**/workflow/**/*.json",
        "**/workspace/**/*.json",
        "**/workflow_state/**/*.json",
        "**/workflow_action_master/**/*.json",
    ]
    
    files = []
    for pattern in patterns:
        files.extend(APP_ROOT.glob(pattern))
    
    # Exclude .vscode and other non-Frappe directories
    files = [f for f in files if ".vscode" not in str(f)]
    
    return sorted(set(files))

def load_json_safe(filepath):
    """Safely load JSON file with error handling"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"JSON decode error: {e}"
    except Exception as e:
        return None, f"Error: {e}"

def check_doctype_field(data, filepath):
    """Check if JSON has required 'doctype' field"""
    issues = []
    
    if not isinstance(data, dict):
        issues.append("Root is not a JSON object")
        return issues
    
    if 'doctype' not in data:
        issues.append("Missing required 'doctype' field")
    
    return issues

def check_doctype_references(data, filepath):
    """Check if referenced DocTypes are valid (basic check)"""
    issues = []
    
    if not isinstance(data, dict):
        return issues
    
    for field in DOCTYPE_REFERENCE_FIELDS:
        if field in data:
            value = data[field]
            if value and isinstance(value, str):
                # Basic validation: should not be empty and should be reasonable
                if len(value.strip()) == 0:
                    issues.append(f"Field '{field}' is empty")
                elif value.startswith(" ") or value.endswith(" "):
                    issues.append(f"Field '{field}' has leading/trailing spaces: '{value}'")
    
    return issues

def get_component_type(filepath):
    """Determine component type from file path"""
    path_str = str(filepath)
    if "/notification/" in path_str:
        return "Notification"
    elif "/dashboard_chart/" in path_str:
        return "Dashboard Chart"
    elif "/report/" in path_str:
        return "Report"
    elif "/print_format/" in path_str:
        return "Print Format"
    elif "/workflow/" in path_str and "/workflow_state/" not in path_str and "/workflow_action_master/" not in path_str:
        return "Workflow"
    elif "/workspace/" in path_str:
        return "Workspace"
    elif "/workflow_state/" in path_str:
        return "Workflow Document State"
    elif "/workflow_action_master/" in path_str:
        return "Workflow Action Master"
    else:
        return "Unknown"

def audit_all_json_files():
    """Main audit function"""
    print("=" * 80)
    print("JSON SCHEMA AUDIT REPORT")
    print("=" * 80)
    print()
    
    files = find_all_json_components()
    print(f"Found {len(files)} JSON component files to audit\n")
    
    # Statistics
    stats = defaultdict(int)
    issues_by_file = {}
    issues_by_type = defaultdict(list)
    
    for filepath in files:
        relative_path = filepath.relative_to(APP_ROOT)
        component_type = get_component_type(filepath)
        stats[f"total_{component_type}"] += 1
        
        # Load JSON
        data, load_error = load_json_safe(filepath)
        if load_error:
            issue = f"[{component_type}] {relative_path}: {load_error}"
            issues_by_file[str(relative_path)] = [load_error]
            issues_by_type[component_type].append(issue)
            stats["files_with_errors"] += 1
            continue
        
        # Check for issues
        file_issues = []
        
        # Check doctype field
        doctype_issues = check_doctype_field(data, filepath)
        file_issues.extend(doctype_issues)
        
        # Check DocType references
        reference_issues = check_doctype_references(data, filepath)
        file_issues.extend(reference_issues)
        
        if file_issues:
            issues_by_file[str(relative_path)] = file_issues
            for issue in file_issues:
                issues_by_type[component_type].append(f"{relative_path}: {issue}")
            stats["files_with_issues"] += 1
        else:
            stats["files_ok"] += 1
    
    # Print summary statistics
    print("SUMMARY STATISTICS")
    print("-" * 80)
    print(f"Total files scanned: {len(files)}")
    print(f"Files OK: {stats['files_ok']}")
    print(f"Files with issues: {stats['files_with_issues']}")
    print(f"Files with load errors: {stats['files_with_errors']}")
    print()
    
    # Print component type breakdown
    print("COMPONENT TYPE BREAKDOWN")
    print("-" * 80)
    for key in sorted(stats.keys()):
        if key.startswith("total_"):
            comp_type = key.replace("total_", "")
            count = stats[key]
            print(f"{comp_type}: {count}")
    print()
    
    # Print issues by type
    if issues_by_type:
        print("ISSUES BY COMPONENT TYPE")
        print("-" * 80)
        for comp_type in sorted(issues_by_type.keys()):
            issues = issues_by_type[comp_type]
            print(f"\n{comp_type} ({len(issues)} issues):")
            for issue in issues[:10]:  # Limit to first 10
                print(f"  - {issue}")
            if len(issues) > 10:
                print(f"  ... and {len(issues) - 10} more")
        print()
    
    # Print detailed issues
    if issues_by_file:
        print("DETAILED ISSUES")
        print("-" * 80)
        for filepath in sorted(issues_by_file.keys())[:20]:  # Limit to first 20
            issues = issues_by_file[filepath]
            print(f"\n{filepath}:")
            for issue in issues:
                print(f"  - {issue}")
        
        if len(issues_by_file) > 20:
            print(f"\n... and {len(issues_by_file) - 20} more files with issues")
        print()
    
    # Final verdict
    print("=" * 80)
    if stats["files_with_issues"] == 0 and stats["files_with_errors"] == 0:
        print("✅ ALL JSON SCHEMAS PASSED AUDIT")
    else:
        print(f"⚠️  FOUND ISSUES IN {stats['files_with_issues'] + stats['files_with_errors']} FILES")
    print("=" * 80)
    
    return stats["files_with_issues"] + stats["files_with_errors"]

if __name__ == "__main__":
    issues_count = audit_all_json_files()
    sys.exit(0 if issues_count == 0 else 1)
