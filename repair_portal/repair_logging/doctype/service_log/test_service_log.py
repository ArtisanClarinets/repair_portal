# File: repair_logging/doctype/service_log/test_service_log.py
# Updated: 2025-06-14
# Version: 1.0
# Purpose: Tests for Service Log doctype.

import unittest

import frappe


class TestServiceLog(unittest.TestCase):
    def test_service_log_creation(self):
        doc = frappe.get_doc(
            {
                'doctype': 'Service Log',
                'instrument_profile': 'TEST-INSTRUMENT',
                'service_type': 'Repair',
                'description': 'Complete key overhaul.',
                'performed_by': 'Administrator',
                'date': '2025-06-14',
            }
        )
        doc.insert(ignore_permissions=True)
        self.assertEqual(doc.service_type, 'Repair')
        self.assertEqual(doc.description, 'Complete key overhaul.')
        self.assertIsNotNone(doc.name)
