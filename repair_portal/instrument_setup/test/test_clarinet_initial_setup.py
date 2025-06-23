import unittest

import frappe


class TestClarinetInitialSetup(unittest.TestCase):
    def setUp(self):
        if not frappe.db.exists('Customer', 'test@example.com'):
            frappe.get_doc(
                {
                    'doctype': 'Customer',
                    'customer_name': 'Test Customer',
                    'email_id': 'test@example.com',
                }
            ).insert()
        if not frappe.db.exists('Item', 'CLARINET01'):
            frappe.get_doc(
                {
                    'doctype': 'Item',
                    'item_code': 'CLARINET01',
                    'item_group': 'Clarinets',
                    'item_name': 'Test Clarinet',
                }
            ).insert()

        self.intake = frappe.get_doc(
            {
                'doctype': 'Clarinet Intake',
                'serial_number': 'CLT-0001',
                'item_code': 'CLARINET01',
                'customer': 'test@example.com',
                'received_date': frappe.utils.today(),
            }
        ).insert()

        self.inspection = frappe.get_doc(
            {
                'doctype': 'Clarinet Inspection',
                'intake': self.intake.name,
                'inspection_date': frappe.utils.today(),
                'technician': frappe.session.user,
                'status': 'Pass',
            }
        ).insert()

    def test_setup_triggers_stock_and_invoice(self):
        setup = frappe.get_doc(
            {
                'doctype': 'Clarinet Initial Setup',
                'inspection': self.inspection.name,
                'setup_date': frappe.utils.today(),
                'technician': frappe.session.user,
                'status': 'Pass',
                'materials_used': [
                    {'item': 'CLARINET01', 'quantity': 1, 'source_warehouse': 'Stores - TC'}
                ],
            }
        )
        setup.insert()
        setup.submit()

        assert frappe.db.exists('Stock Entry', {'custom_source_setup': setup.name})
        assert frappe.db.exists('Serial No', {'serial_no': self.intake.serial_number})
        assert frappe.db.exists('Asset', {'custom_clarinet_setup': setup.name})
        assert frappe.db.exists('Sales Invoice Item', {'item_code': 'CLARINET01'})
