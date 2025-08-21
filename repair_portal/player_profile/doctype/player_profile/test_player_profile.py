# File Header Template
# Relative Path: repair_portal/player_profile/doctype/player_profile/test_player_profile.py
# Last Updated: 2025-07-20
# Version: v2.0
# Purpose: Automated test stub for Player Profile Doctype, covering CRUD, business logic, and linkage for Fortune-500 CRM quality.
# Dependencies: frappe, Player Profile, Instrument Profile, Sales Invoice

import unittest

import frappe


class TestPlayerProfile(unittest.TestCase):
	def setUp(self):
		# Minimal creation for Player Profile
		self.profile = frappe.get_doc(
			{
				"doctype": "Player Profile",
				"player_name": "Unit Test Player",
				"primary_email": "unitest@example.com",
				"player_level": "Professional (Orchestral)",
			}
		)
		self.profile.insert()

	def test_crud(self):
		# Fetch and update
		p = frappe.get_doc("Player Profile", self.profile.name) # type: ignore
		p.preferred_reed_brand = "Vandoren" # type: ignore
		p.save()
		self.assertEqual(frappe.get_doc("Player Profile", p.name).preferred_reed_brand, "Vandoren") # type: ignore

	def test_lifetime_value_calculation(self):
		# Simulate a Sales Invoice link and check CLV update
		invoice = frappe.get_doc(
			{
				"doctype": "Sales Invoice",
				"customer": "Test Customer",
				"player_profile": self.profile.name,
				"grand_total": 1000.00,
				"docstatus": 1,
			}
		)
		invoice.insert()
		self.profile._calc_lifetime_value() # type: ignore
		self.assertGreaterEqual(self.profile.customer_lifetime_value, 1000) # type: ignore

	def tearDown(self):
		frappe.delete_doc("Player Profile", self.profile.name, ignore_permissions=True)
		# Clean up invoices
		for invoice in frappe.get_all("Sales Invoice", filters={"player_profile": self.profile.name}):
			frappe.delete_doc("Sales Invoice", invoice["name"], ignore_permissions=True)
