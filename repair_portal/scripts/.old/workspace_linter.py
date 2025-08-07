# tools/workspace_linter.py
# Updated: 2025-06-11
# Version: 1.1
# Purpose: Validate workspace JSON files for required fields and Frappe best practices

import json
import os
import sys

REQUIRED_TOP_LEVEL = ["doctype", "name", "label", "module", "type", "public"]
BEST_PRACTICE_WARNINGS = {"content": "❌ Deprecated: 'content' field is no longer used in Frappe v15."}

OPTIONAL_SECTIONS = ["sections", "cards", "charts", "onboarding", "filters"]


def lint_workspace(file_path):
    problems = []
    try:
        with open(file_path, encoding="utf-8") as f:
            doc = json.load(f)

        # Check required fields
        for field in REQUIRED_TOP_LEVEL:
            if field not in doc:
                problems.append(f"❗ Missing required field: {field}")

        # Check deprecated/bad practice
        for field in BEST_PRACTICE_WARNINGS:
            if field in doc:
                problems.append(BEST_PRACTICE_WARNINGS[field])

        # Check layout completeness
        if not doc.get("sections") and not doc.get("cards"):
            problems.append("⚠️ Workspace has no 'sections' or 'cards' defined.")

        # Optional section tips
        for field in OPTIONAL_SECTIONS:
            if field not in doc:
                problems.append(f"ℹ️ Consider adding optional '{field}' field for completeness.")

    except Exception as e:
        problems.append(f"❌ Invalid JSON or file error: {e}")

    return problems


def lint_all(base_dir):
    summary = {}
    for root, _dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".json") and "workspace" in root:
                full_path = os.path.join(root, file)
                issues = lint_workspace(full_path)
                if issues:
                    summary[full_path] = issues
    return summary


if __name__ == "__main__":
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "../repair_portal"
    print(f"🔍 Linting workspace JSONs in: {base_dir}")
    result = lint_all(base_dir)

    if result:
        for file, issues in result.items():
            print(f"\n📄 {file}:")
            for issue in issues:
                print(f" - {issue}")
        print("\n❗ Linting completed with issues.")
    else:
        print("✅ All workspace JSONs passed lint check.")
