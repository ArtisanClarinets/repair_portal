import os
import json
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent / 'repair_portal/repair_portal'

missing_py_files = []
mismatched_class_names = []
missing_json_files = []

print('\nPre-Migrate Check Report')
print('==========================')

for root, dirs, files in os.walk(APP_DIR):
    for file in files:
        if file.endswith('.json') and 'doctype' in root:
            doctype_path = Path(root)
            doctype_name = doctype_path.name
            py_path = doctype_path / f'{doctype_name}.py'
            json_path = doctype_path / f'{doctype_name}.json'

            if not py_path.exists():
                missing_py_files.append(str(py_path))

            if not json_path.exists():
                missing_json_files.append(str(json_path))

            # Check for valid controller class
            expected_class_name = ''.join(word.capitalize() for word in doctype_name.split('_'))
            if py_path.exists():
                with open(py_path) as f:
                    content = f.read()
                    if f'class {expected_class_name}(Document)' not in content:
                        mismatched_class_names.append((str(py_path), expected_class_name))

# Output results
if missing_py_files:
    print('❌ Missing Python Controller Files:')
    for path in missing_py_files:
        print(f' - {path}')
else:
    print('✅ All controller files found.')

if mismatched_class_names:
    print('❌ Mismatched Controller Class Names:')
    for path, expected in mismatched_class_names:
        print(f' - {path}: should define `class {expected}(Document)`')
else:
    print('✅ All controller class names are valid.')

if missing_json_files:
    print('❌ Missing Doctype JSON Files:')
    for path in missing_json_files:
        print(f' - {path}')
else:
    print('✅ All Doctype JSON files found.')

print('\n✔ Use this report before any install or migration.')
