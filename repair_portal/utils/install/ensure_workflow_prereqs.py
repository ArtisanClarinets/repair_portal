# -*- coding: utf-8 -*-
"""
Idempotently ensures all Workflow Actions and Workflow States exist (v15-safe).
Place: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/utils/install/ensure_workflow_prereqs.py
Hook:  after_migrate = ["repair_portal.utils.install.ensure_workflow_prereqs.ensure_workflow_prereqs"]
"""

from __future__ import annotations
import frappe

# ---- COMPLETE SET (from your app analysis) ----
ACTIONS = [
    "Activate","Approve","Archive","Attach Customer","Begin Inspection","Close","Close and Archive","Complete",
    "Complete Repair/Setup","Confirm Delivery","Customer Approves","Customer Rejects","Delete","Deliver","Fail",
    "Flag Damage","Pass","Process Payment & Ship","Ready for Pickup","Reinspect","Reopen","Return to Draft","Start",
    "Start Work","Submit","Submit Client Info","Attach Instrument","Detach Instrument","Attach Player","Detach Player",
    "Attach Vendor","Detach Vendor","Confirm Return"
]

# style: Success | Warning | Danger | Primary | Inverse | Info (or None)
STATES = [
    ("Active","Primary"),
    ("Approved","Success"),
    ("Archived","Inverse"),
    ("Available",None),
    ("Awaiting Customer Approval","Warning"),
    ("Awaiting Payment","Warning"),
    ("Awaiting Pickup","Info"),
    ("Checked In",None),
    ("Checked Out",None),
    ("Closed",None),
    ("Complete","Success"),
    ("Deleted",None),
    ("Delivered","Success"),
    ("Draft","Inverse"),
    ("Failed","Danger"),
    ("Flagged","Warning"),
    ("Hold","Warning"),
    ("In Progress","Primary"),
    ("Inspection","Info"),
    ("Loaned",None),
    ("Open","Primary"),
    ("Out for Calibration","Info"),
    ("Passed","Success"),
    ("Pending","Warning"),
    ("Pending Review","Warning"),
    ("Ready for Pickup","Info"),
    ("Received","Primary"),
    ("Repair","Primary"),
    ("Returned to Customer","Inverse"),
    ("Setup","Info"),
    ("Submitted",None),
    ("Waiting on Client","Warning"),
]

def ensure_workflow_prereqs():
    ensure_actions()
    ensure_states()

def ensure_actions():
    for nm in ACTIONS:
        if not frappe.db.exists("Workflow Action Master", nm):
            doc = frappe.get_doc({
                "doctype": "Workflow Action Master",
                "workflow_action_name": nm
            })
            doc.insert(ignore_permissions=True)

def ensure_states():
    for nm, style in STATES:
        if frappe.db.exists("Workflow State", nm):
            if style:
                st = frappe.get_doc("Workflow State", nm)
                if st.style != style:
                    st.style = style
                    st.save(ignore_permissions=True)
        else:
            doc = frappe.get_doc({
                "doctype": "Workflow State",
                "workflow_state_name": nm,
                **({"style": style} if style else {})
            })
            doc.insert(ignore_permissions=True)
