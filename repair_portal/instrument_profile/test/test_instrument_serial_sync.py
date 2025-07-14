# File Header Template
# Relative Path: repair_portal/instrument_profile/test/test_instrument_serial_sync.py
# Last Updated: 2025-07-13
# Version: v1.2
# Purpose: Test that Instrument Profile auto-links ERPNext Serial No correctly on update.
# Dependencies: Instrument Profile, Serial No (ERPNext), Item

import frappe
import unittest
from frappe.test_runner import make_test_objects

# Prevent auto-generation of test records for this Doctype
test_records = []

class TestInstrumentSerialSync(unittest.TestCase):

    def setUp(self):
        # Ensure required Item exists
        if not frappe.db.exists('Item', 'CLARINET-A'):
            frappe.get_doc({
                'doctype': 'Item',
                'item_code': 'CLARINET-A',
                'item_name': 'Clarinet Model A',
                'stock_uom': 'Nos',
                'is_stock_item': 1,
                'has_serial_no': 1
            }).insert(ignore_permissions=True)

        self.serial_no = frappe.get_doc({
            'doctype': 'Serial No',
            'serial_no': 'SYNC-TEST-123',
            'item_code': 'CLARINET-A'
        }).insert(ignore_permissions=True)

        self.instrument = frappe.get_doc({
            'doctype': 'Instrument Profile',
            'make': 'Yamaha',
            'model': 'Custom A',
            'serial_number': 'SYNC-TEST-123',
        }).insert(ignore_permissions=True)

    def test_serial_sync(self):
        self.instrument.reload()
        self.assertEqual(self.instrument.erpnext_serial_no, 'SYNC-TEST-123')

    def tearDown(self):
        frappe.delete_doc('Instrument Profile', self.instrument.name, ignore_permissions=True)
        frappe.delete_doc('Serial No', self.serial_no.name, ignore_permissions=True)
        # Optionally cleanup item
        # frappe.delete_doc('Item', 'CLARINET-A', ignore_permissions=True)