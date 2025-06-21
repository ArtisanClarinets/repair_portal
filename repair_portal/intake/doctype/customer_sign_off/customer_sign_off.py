# File: repair_portal/repair_portal/intake/doctype/customer_sign_off/customer_sign_off.py
# Updated: 2025-06-20
# Version: 1.3
# Purpose: Backend logic for Customer Sign Off form submission
# Adds: Notification, attach PDF, log signature to linked DocType table

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class CustomerSignOff(Document):
    def before_submit(self):
        if not self.ip_address:
            self.ip_address = frappe.local.request_ip
        if not self.signed_at:
            self.signed_at = now_datetime()
        if not self.signature_hash:
            self.signature_hash = frappe.generate_hash(length=20)
        if hasattr(self, 'workflow_state') and self.workflow_state != 'Approved':
            self.workflow_state = 'Approved'

    def validate(self):
        if not self.signature_hash:
            frappe.throw("Signature is required to submit.")

    def on_submit(self):
        recipients = []
        if self.owner:
            recipients.append(self.owner)
        if hasattr(self, 'assigned_to') and self.assigned_to:
            recipients.append(self.assigned_to)
        if recipients:
            frappe.sendmail(
                recipients=recipients,
                subject="Customer Sign-Off Submitted",
                message=f"A customer has signed off repair. Record ID: {self.name}",
                reference_doctype=self.doctype,
                reference_name=self.name
            )

        # Attach PDF print
        pdf = frappe.get_print(
            self.doctype,
            self.name,
            print_format='Customer Sign Off PDF',
            as_pdf=True
        )
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"CustomerSignOff_{self.name}.pdf",
            "attached_to_doctype": self.doctype,
            "attached_to_name": self.name,
            "is_private": 1,
            "content": pdf
        })
        file_doc.insert(ignore_permissions=True)

        # Append to Signature Archive if target supports it
        if self.reference_doctype and self.reference_name:
            try:
                ref_doc = frappe.get_doc(self.reference_doctype, self.reference_name)
                if hasattr(ref_doc, 'signature_archive'):
                    ref_doc.append("signature_archive", {
                        "signed_at": self.signed_at,
                        "ip_address": self.ip_address,
                        "signature_hash": self.signature_hash,
                        "signature_image": self.signature_image,
                        "attached_pdf": file_doc.name,
                        "notes": f"Auto-added via sign off {self.name}"
                    })
                    ref_doc.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"SignOff Archive Error [{self.reference_doctype} | {self.reference_name}]")