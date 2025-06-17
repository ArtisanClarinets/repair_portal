# File: repair_portal/service_planning/doctype/service_order_tracker/service_order_tracker.py
# Updated: 2025-06-16
# Version: 1.1
# Purpose: Auto-email status link when Service Order Tracker is created

import frappe
from frappe.model.document import Document


class ServiceOrderTracker(Document):
    def after_insert(self):
        try:
            repair_log = frappe.get_doc("Clarinet Repair Log", self.repair_log)
            if repair_log.customer_email:
                link = f"{frappe.utils.get_url()}/repair-status?name={self.name}"
                subject = "Repair Status Tracker"
                message = f"""
                <p>Dear Customer,</p>
                <p>You can track the status of your clarinet repair using the link below:</p>
                <p><a href=\"{link}\" target=\"_blank\">View Repair Status</a></p>
                <p>Sincerely,<br>MRW Artisan Instruments</p>
                """
                frappe.sendmail(
                    recipients=repair_log.customer_email,
                    subject=subject,
                    message=message
                )
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Tracker Email Failure")