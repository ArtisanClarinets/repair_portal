# File: repair_portal/repair_portal/doctype/pwa_device_registration/pwa_device_registration.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Manages device tokens for PWA push notifications.

import frappe
from frappe.model.document import Document

class PWADeviceRegistration(Document):
    def validate(self):
        if not self.device_token:
            frappe.throw("Device Token is required.")