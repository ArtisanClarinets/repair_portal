import json
import os
import sys

# The complete list of valid DocType names from your bench console output
# Using a set for fast lookups
VALID_DOCTYPES_SET = {
    'Appointment',
    'Print Heading',
    'Instrument Tracker',
    'Player Profile',
    'Instrument_profile',
    'Upgrade Option',
    'Customer Upgrade Request',
    'Tool Calibration Log',
    'Tool',
    'Service Plan',
    'Service Task',
    'Instrument Interaction Log',
    'Tool Usage Log',
    'Clarinet Repair Log',
    'Related Instrument Interaction',
    'Repair Task Log',
    'Instrument Condition Record',
    'Clarinet Setup Log',
    'Material Usage',
    'Setup Template',
    'Setup Checklist Item',
    'Clarinet Initial Setup',
    'Clarinet Inspection',
    'Clarinet Setup Operation',
    'Inspection Finding',
    'Clarinet Intake',
    'Customer Consent Form',
    'Loaner Instrument',
    'Loaner Return Check',
    'Intake Checklist Item',
    'Inspection Template',
    'Inspection Checklist Section',
    'Inspection Checklist Item',
    'Clarinet Condition Assessment',
    'Repair Order',
    'Repair Task',
    'Repair Order Settings',
    'final_qa_checklist',
    'final_qa_checklist_item',
    'service_log',
}

# Define required fields for each config/document type
REQUIRED_FIELDS = {
    'doctype': ['doctype', 'name'],
    'report': ['doctype', 'name', 'ref_doctype', 'report_type'],
    'workflow': ['doctype', 'name', 'workflow_name', 'document_type', 'states', 'transitions'],
    'dashboard_chart': ['doctype', 'name', 'chart_name', 'chart_type', 'document_type'],
    'list_dashboard': ['doctype', 'name'],
    'notification': ['doctype', 'name'],
    'workspace': ['doctype', 'name', 'label'],
    'module_def': ['doctype', 'name'],
    'number_card': ['doctype', 'name'],
    'custom_script': ['doctype', 'name'],
    'web_form': ['doctype', 'name'],
    'print_format': ['doctype', 'name'],
}


def get_doc_category_and_type(file_path):
    path_parts = file_path.split(os.sep)
    for category in REQUIRED_FIELDS:
        if category in path_parts:
            return category
    return None


def validate_fields(data, required_fields, file_path):
    missing = [field for field in required_fields if field not in data]
    return [f'❌ {file_path}: Missing required field(s): {missing}'] if missing else []


def validate_by_category(category, data, file_path):
    errors = validate_fields(data, REQUIRED_FIELDS[category], file_path)
    if category == 'doctype':
        if data.get('doctype') == 'DocType':
            name = data.get('name')
            if name and name not in VALID_DOCTYPES_SET:
                errors.append(f"❌ {file_path}: Unregistered DocType '{name}'")
    return errors


def scan_all_jsons(app_root_path):
    errors = []
    found = False
    for dirpath, _, filenames in os.walk(app_root_path):
        for fname in filenames:
            if fname.endswith('.json'):
                file_path = os.path.join(dirpath, fname)
                found = True
                try:
                    with open(file_path, encoding='utf-8') as f:
                        data = json.load(f)
                    category = get_doc_category_and_type(file_path)
                    if category:
                        errs = validate_by_category(category, data, file_path)
                        errors.extend(errs)
                except json.JSONDecodeError:
                    errors.append(f'🚫 Invalid JSON format in: {file_path}')
                except Exception as e:
                    errors.append(f'⚠️ Error processing {file_path}: {str(e)}')
    if not found:
        print(f'⚠️ No JSON files found under {app_root_path}')
        return 1
    if errors:
        print('\n'.join(errors))
        print(f'\n❌ Validation failed: {len(errors)} errors found.')
        return 1
    else:
        print('✅ All JSON files are compliant with required fields for their DocType/Config type.')
        return 0


if __name__ == '__main__':
    APP_ROOT_PATH = '/opt/frappe/erp-bench/apps/repair_portal/repair_portal'
    sys.exit(scan_all_jsons(APP_ROOT_PATH))
