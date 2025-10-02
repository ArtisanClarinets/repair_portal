"""
Backfills 'workflow_state' from legacy fields when values match existing Workflow State names.
Run: bench execute repair_portal.utils.workflows.backfill_workflow_state:run --kwargs '{"doctype":"Clarinet Intake","legacy_fields":["intake_status","status"]}'
"""
from __future__ import annotations

import frappe


def run(doctype: str, legacy_fields: list[str]):
    states = set(x.name for x in frappe.get_all("Workflow State", fields=["name"]))
    names = frappe.get_all(doctype, pluck="name")
    updated = 0
    for n in names:
        doc = frappe.get_doc(doctype, n)
        if getattr(doc, "workflow_state", None):
            continue
        for lf in legacy_fields:
            val = getattr(doc, lf, None)
            if val and val in states:
                doc.db_set("workflow_state", val, update_modified=False)
                updated += 1
                break
    frappe.msgprint(f"{doctype}: backfilled workflow_state on {updated} records.")
    return {"doctype": doctype, "updated": updated}

