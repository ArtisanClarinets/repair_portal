# File: repair_portal/enhancements/doctype/customer_sign_off/customer_sign_off.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Server-side logic for Customer Sign Off DocType

import frappe
from frappe.model.document import Document


class CustomerSignOff(Document):
    def validate(self):
        if self.approval_status == "Approved" and not self.signature:
            frappe.throw("Signature must be attached when approving.")

    def on_submit(self):
        if self.approval_status == "Approved":
            frappe.msgprint("Sign-off approved. Shipping label may now be released.")