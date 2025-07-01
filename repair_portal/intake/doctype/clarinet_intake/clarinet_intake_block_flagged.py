# Server Script to block edits and cancels in Flagged state
# /opt/frappe/erp-bench/apps/repair_portal/repair_portal/intake/doctype/clarinet_intake/clarinet_intake_block_flagged.py

import frappe


def before_save(doc, method=None):
    if doc.workflow_state == "Flagged":
        frappe.throw("You must revert this Intake from 'Flagged' to 'QC' before editing.")


def before_cancel(doc, method=None):
    if doc.workflow_state == "Flagged":
        frappe.throw("You must revert this Intake from 'Flagged' to 'QC' before cancelling.")
