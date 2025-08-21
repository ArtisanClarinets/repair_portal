# File: repair_portal/repair/tests/test_repair_order.py
# Last Updated: 2025-07-14
# Version: v2.0
# Purpose: Minimal unit test for unified Repair Order doctype
# Dependencies: frappe, Repair Order

import unittest

import frappe


class TestRepairOrder(unittest.TestCase):
	def test_create_minimal_repair_order(self):
		doc = frappe.get_doc(
			{
				"doctype": "Repair Order",
				"customer": "Test Customer",
				"issue_description": "Example problem",
			}
		)
		doc.insert(ignore_permissions=True)
		self.assertTrue(doc.name)
		self.assertEqual(doc.customer, "Test Customer") # type: ignore
		self.assertEqual(doc.issue_description, "Example problem") # type: ignore
		# Clean up
		frappe.delete_doc("Repair Order", doc.name)
