# File Header Template
# Relative Path: repair_portal/repair_portal/patches/v15_merge_repair_request_to_repair_order.py
# Last Updated: 2025-07-14
# Version: v1.0
# Purpose: Data migration from Repair Request to Repair Order (schema merge)
# Dependencies: Repair Order, Repair Request, Repair Note, Qa Checklist Item

import frappe

def execute():
    """
    Migrates all Repair Request records and children to the unified Repair Order doctype.
    Safe to re-run; will skip records already migrated.
    """
    req_list = frappe.get_all("Repair Request", fields=["*"])
    count = 0
    for req in req_list:
        if frappe.db.exists("Repair Order", req.name):
            continue  # Already migrated

        # Map fields to Repair Order
        doc = frappe.new_doc("Repair Order")
        doc.name = req.name
        doc.customer = req.customer
        doc.instrument_category = req.instrument_category
        doc.date_reported = req.date_reported
        doc.promise_date = req.promise_date
        doc.issue_description = req.issue_description
        doc.technician_assigned = req.technician_assigned
        doc.priority_level = req.priority_level
        doc.status = req.status
        # Copy other custom fields if needed
        # Link children: repair_notes
        notes = frappe.get_all("Repair Note", filters={"parent": req.name, "parenttype": "Repair Request"}, fields=["*"])
        for note in notes:
            note.pop("name", None)
            doc.append("repair_notes", note)
        # Link QA checklist
        qa_items = frappe.get_all("Qa Checklist Item", filters={"parent": req.name, "parenttype": "Repair Request"}, fields=["*"])
        for item in qa_items:
            item.pop("name", None)
            doc.append("qa_checklist", item)
        doc.insert(ignore_permissions=True)
        count += 1
    frappe.msgprint(f"{count} Repair Requests migrated to Repair Order. Review status and close old requests when confirmed.")
