# /repair_portal/scripts/fix_workspace_fixtures.py
# Updated: 2025-06-11
# Version: 1.0
# Purpose: Ensure Workspace fixtures use stringified 'content' to comply with Frappe v15.

import json

FIXTURE_PATH = 'apps/repair_portal/repair_portal/fixtures/workspace.json'

with open(FIXTURE_PATH, 'r+') as f:
    data = json.load(f)
    changed = False
    for doc in data:
        if doc.get('doctype') == 'Workspace' and isinstance(doc.get('content'), list):
            doc['content'] = json.dumps(doc['content'])
            changed = True
    if changed:
        f.seek(0)
        json.dump(data, f, indent=1)
        f.truncate()

print('Workspace fixture content fields stringified for Frappe v15 compliance.')
