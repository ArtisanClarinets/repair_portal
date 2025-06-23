import json

import frappe


def execute():
    workspace_blocks = {
        'intake-workspace': [
            {'type': 'doctype', 'name': 'Instrument Intake Form', 'label': 'Intake Form', 'col': 6}
        ],
        'inspection-workspace': [
            {
                'type': 'doctype',
                'name': 'Clarinet Condition Assessment',
                'label': 'Assessment',
                'col': 6,
            }
        ],
        'service-planning-workspace': [
            {'type': 'doctype', 'name': 'Service Plan', 'label': 'Plans', 'col': 6}
        ],
        'repair-logging-workspace': [
            {'type': 'doctype', 'name': 'Repair Task Log', 'label': 'Repairs', 'col': 6},
            {'type': 'report', 'name': 'Repair Summary', 'doctype': 'Repair Task Log', 'col': 6},
            {'type': 'chart', 'name': 'Open Repairs by Type', 'col': 12},
        ],
        'qa-workspace': [
            {'type': 'doctype', 'name': 'Final QA Checklist', 'label': 'QA Checklist', 'col': 6}
        ],
        'repair-tools-workspace': [
            {'type': 'doctype', 'name': 'Tool Usage Log', 'label': 'Tool Log', 'col': 6}
        ],
        'repair-enhancements-workspace': [
            {'type': 'doctype', 'name': 'Customer Upgrade Request', 'label': 'Upgrades', 'col': 6}
        ],
    }

    for ws_name, blocks in workspace_blocks.items():
        if frappe.db.exists('Workspace', ws_name):
            doc = frappe.get_doc('Workspace', ws_name)
            doc.content = json.dumps(blocks)
            doc.save(ignore_permissions=True)

    frappe.db.commit()
