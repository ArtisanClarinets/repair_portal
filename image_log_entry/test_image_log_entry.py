# relative path: repair_portal/instrument_profile/doctype/image_log_entry/test_image_log_entry.py
# updated: 2025-06-15
# version: 1.0
# purpose: Unit tests for the Image Log Entry child table DocType.

import unittest

import frappe


class TestImageLogEntry(unittest.TestCase):
    def test_creation(self):
        doc = frappe.get_doc(
            {
                'doctype': 'Image Log Entry',
                'image': 'test.jpg',
                'tag': 'crack',
                'note': 'Test entry',
            }
        )
        assert doc.tag == 'crack'
        assert doc.note == 'Test entry'
