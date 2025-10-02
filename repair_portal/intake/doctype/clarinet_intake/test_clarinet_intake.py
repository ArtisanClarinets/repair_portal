# Path: repair_portal/intake/doctype/clarinet_intake/test_clarinet_intake.py
# Date: 2025-10-01
# Version: 1.0.0
# Description: Comprehensive test suite for Clarinet Intake DocType; covers validation, automation, workflows, and edge cases.
# Dependencies: frappe, frappe.tests, unittest

from __future__ import annotations

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase


class TestClarinetIntake(FrappeTestCase):
	"""Test suite for Clarinet Intake DocType."""

	def setUp(self):
		"""Set up test data before each test."""
		# Clean up any existing test data
		self.cleanup_test_data()
		
		# Create test dependencies
		self.setup_test_dependencies()

	def tearDown(self):
		"""Clean up after each test."""
		self.cleanup_test_data()

	def cleanup_test_data(self):
		"""Remove test data from database."""
		# Delete test intakes
		frappe.db.delete("Clarinet Intake", {"serial_no": ["like", "TEST_%"]})
		
		# Delete test instruments
		frappe.db.delete("Instrument", {"model": ["like", "TEST_%"]})
		
		# Delete test serial numbers
		frappe.db.delete("Instrument Serial Number", {"serial": ["like", "TEST_%"]})
		
		# Delete test inspections
		frappe.db.delete("Instrument Inspection", {"model": ["like", "TEST_%"]})
		
		# Delete test customers
		frappe.db.delete("Customer", {"customer_name": ["like", "Test Customer%"]})
		
		frappe.db.commit()

	def setup_test_dependencies(self):
		"""Create required test dependencies."""
		# Create test Brand if not exists
		if not frappe.db.exists("Brand", "Test Brand"):
			brand = frappe.get_doc({
				"doctype": "Brand",
				"brand": "Test Brand"
			})
			brand.insert(ignore_if_duplicate=True)
		
		# Create test Instrument Category
		if not frappe.db.exists("Instrument Category", "Clarinet"):
			cat = frappe.get_doc({
				"doctype": "Instrument Category",
				"category_name": "Clarinet",
				"is_active": 1
			})
			cat.insert(ignore_if_duplicate=True)
		
		# Create test Customer for repair intakes
		if not frappe.db.exists("Customer", {"customer_name": "Test Customer Repair"}):
			cust = frappe.get_doc({
				"doctype": "Customer",
				"customer_name": "Test Customer Repair",
				"customer_type": "Individual",
				"customer_group": "All Customer Groups"
			})
			cust.insert()
		
		frappe.db.commit()

	# ============================================================================
	# Test: New Inventory Intake
	# ============================================================================

	def test_new_inventory_intake_creates_all_records(self):
		"""Test that New Inventory intake creates Item, ISN, Instrument, Inspection, and Setup."""
		intake = frappe.get_doc({
			"doctype": "Clarinet Intake",
			"intake_type": "New Inventory",
			"instrument_category": "Clarinet",
			"manufacturer": "Test Brand",
			"model": "TEST_MODEL_001",
			"serial_no": "TEST_SN_001",
			"clarinet_type": "B♭ Clarinet",
			"body_material": "Grenadilla",
			"key_plating": "Silver",
			"item_code": "TEST_ITEM_001",
			"item_name": "Test Clarinet",
			"acquisition_cost": 1000.00,
			"store_asking_price": 1500.00,
		})
		intake.insert()
		
		# Verify intake was created
		self.assertTrue(intake.name)
		self.assertEqual(intake.intake_type, "New Inventory")
		
		# Verify Instrument Serial Number was created
		isn = frappe.db.get_value("Instrument Serial Number", {"serial": "TEST_SN_001"}, "name")
		self.assertTrue(isn, "Instrument Serial Number should be created")
		
		# Verify Instrument was created
		self.assertTrue(intake.instrument, "Instrument should be linked")
		instrument = frappe.get_doc("Instrument", intake.instrument)
		self.assertEqual(instrument.model, "TEST_MODEL_001")
		
		# Verify Instrument Inspection was created
		inspection = frappe.db.get_value("Instrument Inspection", {"intake_record_id": intake.name}, "name")
		self.assertTrue(inspection, "Instrument Inspection should be created")
		
		# Verify Clarinet Initial Setup was created for New Inventory
		setup = frappe.db.get_value("Clarinet Initial Setup", {"intake": intake.name}, "name")
		self.assertTrue(setup, "Clarinet Initial Setup should be created for New Inventory")
		
		# Verify Item was created
		item = frappe.db.get_value("Item", {"item_code": "TEST_ITEM_001"}, "name")
		self.assertTrue(item, "Item should be created")

	def test_new_inventory_required_fields(self):
		"""Test that New Inventory intake enforces required fields."""
		# Missing item_code should fail
		intake = frappe.get_doc({
			"doctype": "Clarinet Intake",
			"intake_type": "New Inventory",
			"instrument_category": "Clarinet",
			"manufacturer": "Test Brand",
			"model": "TEST_MODEL_002",
			"serial_no": "TEST_SN_002",
			"clarinet_type": "B♭ Clarinet",
			# Missing: item_code, item_name, acquisition_cost, store_asking_price
		})
		
		with self.assertRaises(frappe.ValidationError):
			intake.insert()

	# ============================================================================
	# Test: Repair Intake
	# ============================================================================

	def test_repair_intake_creates_inspection_only(self):
		"""Test that Repair intake creates Inspection but not Setup."""
		intake = frappe.get_doc({
			"doctype": "Clarinet Intake",
			"intake_type": "Repair",
			"instrument_category": "Clarinet",
			"manufacturer": "Test Brand",
			"model": "TEST_MODEL_003",
			"serial_no": "TEST_SN_003",
			"clarinet_type": "B♭ Clarinet",
			"customer": frappe.db.get_value("Customer", {"customer_name": "Test Customer Repair"}, "name"),
			"customers_stated_issue": "Pads need replacement",
		})
		intake.insert()
		
		# Verify Instrument Inspection was created
		inspection = frappe.db.get_value("Instrument Inspection", {"intake_record_id": intake.name}, "name")
		self.assertTrue(inspection, "Instrument Inspection should be created")
		
		# Verify Clarinet Initial Setup was NOT created for Repair
		setup = frappe.db.get_value("Clarinet Initial Setup", {"intake": intake.name}, "name")
		self.assertFalse(setup, "Clarinet Initial Setup should NOT be created for Repair")

	def test_repair_intake_required_fields(self):
		"""Test that Repair intake enforces customer and issue fields."""
		# Missing customer should fail
		intake = frappe.get_doc({
			"doctype": "Clarinet Intake",
			"intake_type": "Repair",
			"instrument_category": "Clarinet",
			"manufacturer": "Test Brand",
			"model": "TEST_MODEL_004",
			"serial_no": "TEST_SN_004",
			"clarinet_type": "B♭ Clarinet",
			# Missing: customer, customers_stated_issue
		})
		
		with self.assertRaises(frappe.ValidationError):
			intake.insert()

	# ============================================================================
	# Test: Serial Number Logic
	# ============================================================================

	def test_duplicate_serial_uses_existing_instrument(self):
		"""Test that duplicate serials link to existing Instrument."""
		# Create first intake
		intake1 = frappe.get_doc({
			"doctype": "Clarinet Intake",
			"intake_type": "New Inventory",
			"instrument_category": "Clarinet",
			"manufacturer": "Test Brand",
			"model": "TEST_MODEL_005",
			"serial_no": "TEST_SN_005",
			"clarinet_type": "B♭ Clarinet",
			"body_material": "Grenadilla",
			"item_code": "TEST_ITEM_005",
			"item_name": "Test Clarinet 5",
			"acquisition_cost": 1000.00,
			"store_asking_price": 1500.00,
		})
		intake1.insert()
		first_instrument = intake1.instrument
		
		# Create second intake with same serial
		intake2 = frappe.get_doc({
			"doctype": "Clarinet Intake",
			"intake_type": "Repair",
			"instrument_category": "Clarinet",
			"manufacturer": "Test Brand",
			"model": "TEST_MODEL_005",
			"serial_no": "TEST_SN_005",  # Same serial
			"clarinet_type": "B♭ Clarinet",
			"customer": frappe.db.get_value("Customer", {"customer_name": "Test Customer Repair"}, "name"),
			"customers_stated_issue": "Regular maintenance",
		})
		intake2.insert()
		
		# Second intake should link to same instrument
		self.assertEqual(intake2.instrument, first_instrument, "Should reuse existing Instrument")

	# ============================================================================
	# Test: Validation Logic
	# ============================================================================

	def test_autoname_generates_intake_record_id(self):
		"""Test that intake_record_id is auto-generated."""
		intake = frappe.get_doc({
			"doctype": "Clarinet Intake",
			"intake_type": "New Inventory",
			"instrument_category": "Clarinet",
			"manufacturer": "Test Brand",
			"model": "TEST_MODEL_006",
			"serial_no": "TEST_SN_006",
			"clarinet_type": "B♭ Clarinet",
			"item_code": "TEST_ITEM_006",
			"item_name": "Test Clarinet 6",
			"acquisition_cost": 1000.00,
			"store_asking_price": 1500.00,
		})
		intake.insert()
		
		# Verify intake_record_id was generated
		self.assertTrue(intake.intake_record_id)
		self.assertTrue(intake.intake_record_id.startswith("CI-"))

	# ============================================================================
	# Test: Idempotency
	# ============================================================================

	def test_idempotent_record_creation(self):
		"""Test that repeated saves don't create duplicate child records."""
		intake = frappe.get_doc({
			"doctype": "Clarinet Intake",
			"intake_type": "New Inventory",
			"instrument_category": "Clarinet",
			"manufacturer": "Test Brand",
			"model": "TEST_MODEL_007",
			"serial_no": "TEST_SN_007",
			"clarinet_type": "B♭ Clarinet",
			"item_code": "TEST_ITEM_007",
			"item_name": "Test Clarinet 7",
			"acquisition_cost": 1000.00,
			"store_asking_price": 1500.00,
		})
		intake.insert()
		
		# Count initial child records
		initial_isn_count = frappe.db.count("Instrument Serial Number", {"serial": "TEST_SN_007"})
		initial_instrument_count = frappe.db.count("Instrument", {"model": "TEST_MODEL_007"})
		
		# Save again (should not create duplicates)
		intake.save()
		
		# Verify counts haven't changed
		final_isn_count = frappe.db.count("Instrument Serial Number", {"serial": "TEST_SN_007"})
		final_instrument_count = frappe.db.count("Instrument", {"model": "TEST_MODEL_007"})
		
		self.assertEqual(initial_isn_count, final_instrument_count, "Should not create duplicate ISN")
		self.assertEqual(initial_instrument_count, final_instrument_count, "Should not create duplicate Instrument")


def run_tests():
	"""Run all tests in this module."""
	frappe.db.commit()
	suite = unittest.TestLoader().loadTestsFromTestCase(TestClarinetIntake)
	unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
	run_tests()
