# File: repair_portal/inspection/doctype/inspection_checklist_item/test_inspection_checklist_item.py
# Updated: 2025-06-27
# Purpose: Unit tests for Inspection Checklist Item DocType
import frappe
import unittest

class TestInspectionChecklistItem(unittest.TestCase):
    def test_creation(self):
        item = frappe.new_doc('Inspection Checklist Item')
        item.sequence = 1
        item.area = 'Pad Seal - Top Joint'
        item.criteria = 'Delta P < 0.3 psi'
        item.pass_fail = 'Pass'
        item.severity = 'Minor'
        item.insert()
        self.assertEqual(item.area, 'Pad Seal - Top Joint')
        self.assertEqual(item.pass_fail, 'Pass')
        item.delete()