# File Header Template
# Relative Path: repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Last Updated: 2025-07-13
# Version: v1.0
# Purpose: Handles ERPNext Serial No syncing for instruments
# Dependencies: Serial No (ERPNext), frappe.exceptions

import frappe
from frappe.model.document import Document

class InstrumentProfile(Document):
    def on_update(self):
        # Sync with ERPNext Serial No
        try:
            if self.serial_number:
                serial = frappe.get_doc("Serial No", self.serial_number)
        except frappe.DoesNotExistError:
            try:
                serial = frappe.get_doc({
                    "doctype": "Serial No",
                    "serial_no": self.serial_number,
                    "item_code": self.model or "Generic Instrument",
                    "status": "Active"
                })
                serial.insert(ignore_permissions=True)
            except Exception:
                frappe.log_error(frappe.get_traceback(), "InstrumentProfile: Serial No insert failed")
        else:
            try:
                if serial.item_code != self.model:
                    frappe.msgprint("ERP Serial No model does not match instrument model.")
            except Exception:
                frappe.log_error(frappe.get_traceback(), "InstrumentProfile: Serial No model mismatch")

        try:
            self.erpnext_serial_no = self.serial_number
        except Exception:
            frappe.log_error(frappe.get_traceback(), "InstrumentProfile: Failed linking Serial No")