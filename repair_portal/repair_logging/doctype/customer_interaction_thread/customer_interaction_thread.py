# Path: repair_portal/repair_logging/doctype/customer_interaction_thread/customer_interaction_thread.py
# Date: 2025-06-20
# Version: 1.0.0
# Purpose: Tracks threaded communication per job (Portal, Email, SMS)

import frappe
from frappe.model.document import Document


class CustomerInteractionThread(Document):
    def before_insert(self):
        self.timestamp = frappe.utils.now_datetime()