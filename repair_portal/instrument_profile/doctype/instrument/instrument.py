# Copyright (c) 2025, DT and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Instrument(Document):
    """Instrument Document Model"""
    def validate(self):
        self.check_duplicate_serial_no()

    def check_duplicate_serial_no(self):
        # Avoid duplicate on current document!
        if self.serial_no and frappe.db.exists("Instrument", {"serial_no": self.serial_no, "name": ("!=", self.name)}):
            frappe.log_error(f"Duplicate Serial Number: {self.serial_no} found in Instrument records.")
            frappe.throw(f"Serial Number {self.serial_no} already exists in another Instrument record.")
        return
