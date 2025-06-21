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


    def PWADeviceRegistration(self, device_token=None, device_type=None):
        """
        Initialize a new PWA Device Registration.
        
        :param device_token: The unique token for the device.
        :param device_type: The type of the device (e.g., 'android', 'ios').
        """
        self.device_token = device_token
        self.device_type = device_type
        self.validate()