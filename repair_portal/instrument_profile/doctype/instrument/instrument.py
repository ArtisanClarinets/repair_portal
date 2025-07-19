# Copyright (c) 2025, DT and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Instrument(Document):
    """Instrument Document Model"""

    def check_duplicate_serial_no(self):
        if frappe.db.exists('Instrument', {'serial_no': self.serial_no}):
            frappe.throw(f'Serial Number {self.serial_no} already exists')
            frappe.log_error(
                f'Duplicate Serial Number: {self.serial_no} found in Instrument records.'
            )
        return
