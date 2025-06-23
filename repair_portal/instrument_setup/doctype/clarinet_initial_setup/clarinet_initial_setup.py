# File: repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.py
# Updated: 2025-06-12
# Version: 1.2
# Purpose: Auto-assign technician, trigger stock deduction, and material request creation

import frappe
from frappe.model.document import Document


class ClarinetInitialSetup(Document):
    def before_insert(self):
        if not self.technician:
            available = frappe.get_all(
                'User', filters={'role_profile_name': 'Technician'}, fields=['name'], limit=1
            )
            if available:
                self.technician = available[0].name

    def validate(self):
        for item in self.materials:
            bin_qty = (
                frappe.db.get_value(
                    'Bin', {'item_code': item.item, 'warehouse': item.warehouse}, 'actual_qty'
                )
                or 0
            )
            if item.quantity > bin_qty:
                frappe.throw(f'Insufficient stock for item {item.item}')

    def on_submit(self):
        mr = frappe.new_doc('Material Request')
        mr.material_request_type = 'Material Transfer'
        for item in self.materials:
            mr.append(
                'items',
                {
                    'item_code': item.item,
                    'qty': item.quantity,
                    'schedule_date': frappe.utils.nowdate(),
                    'warehouse': item.warehouse,
                },
            )
        mr.insert()
        frappe.msgprint(f'Auto-created Material Request: {mr.name}')
