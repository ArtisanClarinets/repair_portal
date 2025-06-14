###
# File: repair_portal/command/full_workspace_generator_v15.py
# Last Updated: 2025-06-12
# Version: 1.4
# Purpose: Regenerate workspace JSONs directly based on actual contents of module directories
# Notes:
#   - Normalizes module names from modules.txt to actual folder names
#   - Compliant with ERPNext v15 / Frappe v15 structure
###

import os
import json

APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WORKSPACE_ROOT = os.path.join(APP_ROOT, 'workspace')
MODULES_TXT = os.path.join(APP_ROOT, 'modules.txt')


def normalize_module_name(name):
    return name.lower().replace(' ', '_')


def get_module_names():
    with open(MODULES_TXT, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]


def generate_workspace_json(label):
    return {
        "label": label,
        "items": [],
        "charts": [],
        "shortcuts": [],
        "onboarding": {},
        "links": [],
        "translations": {},
        "creation": None,
        "modified": None
    }


def full_workspace_generate():
    created, updated, skipped, failed = [], [], [], []
    modules = get_module_names()

    for module in modules:
        folder_name = normalize_module_name(module)
        module_dir = os.path.join(APP_ROOT, folder_name)
        if not os.path.isdir(module_dir):
            skipped.append(module)
            continue

        workspace_dir = os.path.join(WORKSPACE_ROOT, folder_name)
        os.makedirs(workspace_dir, exist_ok=True)
        file_path = os.path.join(workspace_dir, f"{folder_name}.json")

        try:
            content = generate_workspace_json(module)
            with open(file_path, 'w') as f:
                json.dump(content, f, indent=4)
            updated.append(module)
        except Exception as e:
            failed.append((module, str(e)))

    print(json.dumps({"created": created, "updated": updated, "skipped": skipped, "failed": failed}, indent=2))