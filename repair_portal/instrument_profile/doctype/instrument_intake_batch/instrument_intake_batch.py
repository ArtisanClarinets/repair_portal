# File: repair_portal/repair_portal/instrument_profile/doctype/instrument_intake_batch/instrument_intake_batch.py
# Updated: 2025-07-14
# Version: 1.1
# Purpose: Automates intake to inventory and instrument profile creation

import frappe
from frappe.model.document import Document


class InstrumentIntakeBatch(Document):
    def on_submit(self):
        for entry in self.entries:
            if self.add_to_inventory:
                self.create_stock_entry(entry)
            if self.create_profiles:
                self.create_instrument_profile(entry)

    def create_stock_entry(self, entry):
        # Example stub: log intent
        frappe.logger().info(f'Would create Stock Entry for serial {entry.serial_no}')

    def create_instrument_profile(self, entry):
        # PATCH: Ensure serial_no exists as Serial No in ERPNext
        if not frappe.db.exists('Serial No', entry.serial_no):
            frappe.throw(f"Serial No '{entry.serial_no}' does not exist in ERPNext!")
        profile = frappe.get_doc(
            {
                'doctype': 'Instrument Profile',
                'serial_no': entry.serial_no,
                'manufacturer': entry.manufacturer,
                'instrument_type': self.instrument_type,
                'status': 'In Inventory',
                'intake_batch': self.name,
            }
        )
        profile.insert()
        frappe.logger().info(f'Created Instrument Profile for {entry.serial_no}')
