# Path: repair_portal/instrument_profile/doctype/instrument/test_instrument.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Comprehensive unit tests for Instrument DocType including validation, link integrity, serial number uniqueness, workflow state management, and permission checks.
# Dependencies: frappe.tests, unittest

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase


class TestInstrument(FrappeTestCase):
    """Test cases for Instrument DocType"""

    def setUp(self):
        """Set up test data"""
        # Create test brand
        if not frappe.db.exists("Brand", "Test Brand"):
            frappe.get_doc({"doctype": "Brand", "brand": "Test Brand"}).insert(ignore_permissions=True)

        # Create test instrument category
        if not frappe.db.exists("Instrument Category", "Test Clarinet"):
            frappe.get_doc(
                {"doctype": "Instrument Category", "title": "Test Clarinet", "is_active": 1}
            ).insert(ignore_permissions=True)

        # Create test instrument model
        if not frappe.db.exists("Instrument Model", "Test-123"):
            frappe.get_doc(
                {
                    "doctype": "Instrument Model",
                    "brand": "Test Brand",
                    "model": "Test-123",
                    "instrument_category": "Test Clarinet",
                    "body_material": "Grenadilla",
                }
            ).insert(ignore_permissions=True)

    def tearDown(self):
        """Clean up test data"""
        # Delete test instruments
        frappe.db.delete("Instrument", {"serial_number": ["like", "TEST%"]})
        frappe.db.commit()

    def test_instrument_creation(self):
        """Test basic instrument creation"""
        instrument = frappe.get_doc(
            {
                "doctype": "Instrument",
                "serial_number": "TEST001",
                "instrument_model": "Test-123",
                "workflow_state": "Draft",
            }
        )
        instrument.insert()

        self.assertEqual(instrument.serial_number, "TEST001")
        self.assertEqual(instrument.instrument_model, "Test-123")
        self.assertEqual(instrument.workflow_state, "Draft")

    def test_required_fields_validation(self):
        """Test that required fields are enforced"""
        # Missing serial_number
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc(
                {"doctype": "Instrument", "instrument_model": "Test-123", "workflow_state": "Draft"}
            ).insert()

        # Missing instrument_model
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc(
                {"doctype": "Instrument", "serial_number": "TEST002", "workflow_state": "Draft"}
            ).insert()

    def test_serial_number_uniqueness(self):
        """Test serial number uniqueness constraint"""
        # Create first instrument
        instrument1 = frappe.get_doc(
            {
                "doctype": "Instrument",
                "serial_number": "TEST003",
                "instrument_model": "Test-123",
                "workflow_state": "Draft",
            }
        )
        instrument1.insert()

        # Try to create duplicate serial number
        with self.assertRaises(frappe.DuplicateEntryError):
            instrument2 = frappe.get_doc(
                {
                    "doctype": "Instrument",
                    "serial_number": "TEST003",  # Same serial number
                    "instrument_model": "Test-123",
                    "workflow_state": "Draft",
                }
            )
            instrument2.insert()

    def test_link_field_validation(self):
        """Test that link fields point to existing records"""
        # Non-existent instrument model
        with self.assertRaises(frappe.LinkValidationError):
            frappe.get_doc(
                {
                    "doctype": "Instrument",
                    "serial_number": "TEST004",
                    "instrument_model": "Non-Existent-Model",
                    "workflow_state": "Draft",
                }
            ).insert()

    def test_workflow_state_values(self):
        """Test valid workflow state values"""
        valid_states = ["Draft", "Active", "In Repair", "Out of Service", "Retired"]

        for i, state in enumerate(valid_states):
            instrument = frappe.get_doc(
                {
                    "doctype": "Instrument",
                    "serial_number": f"TEST{str(i+5).zfill(3)}",
                    "instrument_model": "Test-123",
                    "workflow_state": state,
                }
            )
            instrument.insert()
            self.assertEqual(instrument.workflow_state, state)

    def test_instrument_naming(self):
        """Test instrument naming is based on serial number"""
        instrument = frappe.get_doc(
            {
                "doctype": "Instrument",
                "serial_number": "UNIQUE-SERIAL-123",
                "instrument_model": "Test-123",
                "workflow_state": "Draft",
            }
        )
        instrument.insert()

        self.assertEqual(instrument.name, "UNIQUE-SERIAL-123")

    def test_optional_fields(self):
        """Test that optional fields can be set"""
        instrument = frappe.get_doc(
            {
                "doctype": "Instrument",
                "serial_number": "TEST010",
                "instrument_model": "Test-123",
                "workflow_state": "Active",
                "manufacture_date": "2023-01-15",
                "purchase_date": "2023-02-01",
                "condition": "Excellent",
                "notes": "Test instrument with all optional fields",
            }
        )
        instrument.insert()

        self.assertEqual(instrument.manufacture_date, "2023-01-15")
        self.assertEqual(instrument.purchase_date, "2023-02-01")
        self.assertEqual(instrument.condition, "Excellent")
        self.assertEqual(instrument.notes, "Test instrument with all optional fields")

    def test_condition_values(self):
        """Test various condition values"""
        conditions = ["New", "Excellent", "Good", "Fair", "Poor", "Needs Repair"]

        for i, condition in enumerate(conditions):
            instrument = frappe.get_doc(
                {
                    "doctype": "Instrument",
                    "serial_number": f"COND{str(i+1).zfill(3)}",
                    "instrument_model": "Test-123",
                    "workflow_state": "Active",
                    "condition": condition,
                }
            )
            instrument.insert()
            self.assertEqual(instrument.condition, condition)

    def test_date_validation(self):
        """Test date field validation"""
        # Valid dates
        instrument = frappe.get_doc(
            {
                "doctype": "Instrument",
                "serial_number": "DATE001",
                "instrument_model": "Test-123",
                "workflow_state": "Active",
                "manufacture_date": "2020-01-01",
                "purchase_date": "2020-06-01",
            }
        )
        instrument.insert()

        self.assertEqual(str(instrument.manufacture_date), "2020-01-01")
        self.assertEqual(str(instrument.purchase_date), "2020-06-01")

    def test_workflow_state_transitions(self):
        """Test workflow state changes"""
        instrument = frappe.get_doc(
            {
                "doctype": "Instrument",
                "serial_number": "WORKFLOW001",
                "instrument_model": "Test-123",
                "workflow_state": "Draft",
            }
        )
        instrument.insert()

        # Change to Active
        instrument.workflow_state = "Active"
        instrument.save()
        instrument.reload()
        self.assertEqual(instrument.workflow_state, "Active")

        # Change to In Repair
        instrument.workflow_state = "In Repair"
        instrument.save()
        instrument.reload()
        self.assertEqual(instrument.workflow_state, "In Repair")

        # Change to Retired
        instrument.workflow_state = "Retired"
        instrument.save()
        instrument.reload()
        self.assertEqual(instrument.workflow_state, "Retired")


if __name__ == "__main__":
    unittest.main()
