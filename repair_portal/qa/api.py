"""repair_portal/qa/api.py
Updated: 2025-09-01
Version: 0.1
Purpose: Provide APIs for QA module including customer sign-off.
Dev notes: Called from portal via /api/method/repair_portal.qa.api.*
"""

from __future__ import annotations

import frappe
from frappe.utils import get_request_ip, now


@frappe.whitelist(allow_guest=False, methods=['POST'])
@frappe.only_for(['Client'])
def submit_customer_sign_off(repair: str, signature: str) -> str:
    """Record digital sign-off and mark repair approved."""
    doc = frappe.new_doc('Customer Sign-Off')
    doc.repair = repair
    doc.client = frappe.session.user
    doc.signature = signature
    doc.ip_address = get_request_ip() or frappe.local.request_ip
    doc.signed_on = now()
    doc.approval_state = 'Approved'
    doc.insert(ignore_permissions=True)
    frappe.publish_realtime('customer_sign_off_submitted', {'repair': repair})
    return frappe.safe_json.dumps({'name': doc.name})
