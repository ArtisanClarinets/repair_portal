# Relative Path: repair_portal/repair_logging/doctype/repair_log/test_repair_log.py
# Last Updated: 2025-07-19
# Version: v1.0
# Purpose: Test coverage for Repair Log creation and business logic.
# Dependencies: Repair Log, Instrument, Clarinet Intake, Customer, User

import frappe
import unittest

class TestRepairLog(unittest.TestCase):
    def test_repair_log_creation(self):
        """Create a minimal Repair Log and check core required fields."""
        instrument = frappe.get_all('Instrument', limit=1)
        user = frappe.get_all('User', filters={'enabled': 1}, limit=1)
        if not instrument or not user:
            self.skipTest('Instrument or User not available')
        doc = frappe.get_doc({
            'doctype': 'Repair Log',
            'instrument': instrument[0].name,
            'technician': user[0].name,
            'summary': 'Test Repair',
            'date': frappe.utils.nowdate(),
            'status': 'Open',
        })
        doc.insert(ignore_permissions=True)
        self.assertTrue(doc.name)
        self.assertEqual(doc.status, 'Open')
        self.assertEqual(doc.instrument, instrument[0].name)
        self.assertEqual(doc.technician, user[0].name)
