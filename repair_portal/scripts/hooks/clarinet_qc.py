import json
from pathlib import Path

import frappe

SCHEMA_FILE = Path(__file__).parent.parent / 'data' / 'clarinet_qc.json'


def load_schema():
    with open(SCHEMA_FILE) as f:
        return json.load(f)


def upsert_quality_procedure(proc):
    # Always set both name and quality_procedure_name for ERPNext v15!
    name = proc['name']
    doc = frappe.db.exists('Quality Procedure', {'quality_procedure_name': name})
    doc = frappe.get_doc('Quality Procedure', doc) if doc else frappe.new_doc('Quality Procedure')  # type: ignore
    doc.update(
        {
            'quality_procedure_name': name,
            'item_group': proc.get('item_group'),
            'default_operation': proc.get('default_operation'),
        }
    )
    doc.title = proc.get('title', name)  # use title if available  # type: ignore
    doc.save()
    return name


def sync_qc():
    schema = load_schema()
    # 1. Upsert all procedures (sub first, main last)
    for proc in schema['procedures']:
        upsert_quality_procedure(proc)

    # 2. Set points/steps for each procedure
    for proc in schema['procedures']:
        doc = frappe.get_doc('Quality Procedure', proc['name'])
        child_table = 'processes'  # v15 default, adjust if customized!
        doc.set(child_table, [])  # Clear to idempotently reload

        for pt in proc['points']:
            row = {
                'process_description': pt['parameter'],
                'sequence': pt.get('seq'),
                'tool': pt.get('tool'),
                'acceptance_criteria': pt.get('criteria'),
            }
            if pt.get('sub_procedure'):
                row['sub_procedure'] = pt['sub_procedure']
            doc.append(child_table, row)
        doc.save()

    frappe.db.commit()
    print('✅ Clarinets QC library fully seeded with sub-procedures.')


if __name__ == '__main__':
    sync_qc()
