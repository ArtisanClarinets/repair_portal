# File: repair_portal/enhancements/doctype/service_certificate/service_certificate.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Logic for Service Certificate, includes public URL assignment

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class ServiceCertificate(Document):
    def before_insert(self):
        self.issue_date = nowdate()

    def on_submit(self):
        if not self.certificate_number:
            self.certificate_number = f"CERT-{self.name}"

        base_url = frappe.utils.get_url()
        self.public_url = f"{base_url}/certificate/{self.name}"