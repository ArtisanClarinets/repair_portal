# File Header
# Relative Path: repair_portal/inspection/doctype/instrument_inspection/test_instrument_inspection.py
# Last Updated: 2025-07-26
# Version: v1.0
# Purpose: Comprehensive test suite for the Instrument Inspection DocType.
#          This file tests all server-side logic, including validation rules,
#          business logic on submission, and core model integrity. It covers
#          all inspection types and their unique requirements.

# Standard Python library imports
import unittest

# Frappe framework imports
import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

# Import the class to be tested
from repair_portal.inspection.doctype.instrument_inspection.instrument_inspection import (
    InstrumentInspection,
)


class TestInstrumentInspection(FrappeTestCase):
    """
    Test class for the 'Instrument Inspection' DocType.
    Inherits from FrappeTestCase to leverage its test runner, database transaction
    management, and utility functions.
    """

    def setUp(self):
        """
        Set up the necessary prerequisite documents for the tests.
        This method is run before each test case.
        """
        # Clean up any residual data from previous test runs to ensure isolation
        frappe.db.delete("Instrument Inspection")
        frappe.db.delete("Instrument Profile")
        frappe.db.delete("Serial No", {"serial_no": ["like", "TEST-%"]})
        frappe.db.delete("Customer", {"name": ["like", "Test Customer%"]})

        # Create prerequisite documents
        self.customer = self._create_customer("Test Customer 1")
        self.serial_no_doc = self._create_serial_no("TEST-SN-001")
        # The default 'Administrator' user is used for most tests.

    def tearDown(self):
        """
        Clean up after tests. FrappeTestCase handles DB rollback,
        but this can be used for other cleanup tasks if needed.
        """
        frappe.db.rollback()

    # --- Helper Methods ---

    def _create_serial_no(self, serial, commit=True):
        """Helper to create a 'Serial No' document."""
        if not frappe.db.exists("DocType", "Serial No"):
            # Create a dummy DocType if it doesn't exist in the test environment
            frappe.get_doc({
                "doctype": "DocType",
                "name": "Serial No",
                "module": "Core",
                "custom": 1,
                "fields": [{"label": "Serial No", "fieldname": "serial_no", "fieldtype": "Data"}],
                "permissions": [{"role": "System Manager", "read": 1}]
            }).insert()
            
        doc = frappe.new_doc("Serial No")
        doc.serial_no = serial
        if commit:
            doc.insert(ignore_permissions=True)
        return doc

    def _create_customer(self, name, commit=True):
        """Helper to create a 'Customer' document."""
        if not frappe.db.exists("DocType", "Customer"):
            frappe.get_doc({
                "doctype": "DocType", "name": "Customer", "module": "Selling", "custom": 1,
                "fields": [{"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data"}],
                "permissions": [{"role": "System Manager", "read": 1, "create": 1}]
            }).insert()

        customer = frappe.new_doc("Customer")
        customer.customer_name = name
        if commit:
            customer.insert(ignore_permissions=True)
        return customer

    def _create_inspection(self, **kwargs) -> InstrumentInspection:
        """
        Factory method to create a valid Instrument Inspection document.
        Accepts kwargs to override default values for testing specific scenarios.
        """
        # Define the minimum valid data
        data = {
            "doctype": "Instrument Inspection",
            "inspection_type": "Repair", # A safe default that doesn't trigger complex logic
            "serial_no": self.serial_no_doc.name,
            "inspected_by": "Administrator",
            "customer": self.customer.name,
            "inspection_date": today(),
            **kwargs  # Override defaults with provided arguments
        }
        doc = frappe.get_doc(data)
        return doc

    # --- Test Cases ---

    def test_creation_and_save(self):
        """Test basic creation and saving of an Instrument Inspection record."""
        inspection = self._create_inspection()
        self.assertFalse(inspection.is_new()) # Should be false before insert
        inspection.insert()
        self.assertTrue(inspection.is_new() is False)
        self.assertEqual(inspection.docstatus, 0) # Saved, not submitted
        self.assertIsNotNone(inspection.name)
        
    def test_validate_unique_serial_no(self):
        """Test that the system prevents duplicate active inspections for the same serial number."""
        # Create and save the first inspection
        self._create_inspection(serial_no="TEST-SN-UNIQUE").insert()
        
        # Create a second inspection with the same serial number
        duplicate_inspection = self._create_inspection(serial_no="TEST-SN-UNIQUE")
        
        # Expect a ValidationError upon trying to save the duplicate
        with self.assertRaises(ValidationError) as context:
            duplicate_inspection.insert()
        self.assertIn("already exists for Serial No: TEST-SN-UNIQUE", str(context.exception))

    def test_new_inventory_validation_success(self):
        """Test successful validation for 'New Inventory' type with all required fields."""
        inspection = self._create_inspection(
            inspection_type="New Inventory",
            manufacturer="Buffet Crampon",
            model="R13",
            key="B♭",
            wood_type="Grenadilla",
            customer=None, # Ensure customer fields are empty
            preliminary_estimate=0
        )
        # Should not raise any exception
        inspection.insert()
        self.assertEqual(inspection.inspection_type, "New Inventory")

    def test_new_inventory_missing_required_fields(self):
        """Test validation failure for 'New Inventory' when required fields are missing."""
        inspection = self._create_inspection(
            inspection_type="New Inventory",
            model="R13" # Missing manufacturer, key, wood_type
        )
        with self.assertRaises(ValidationError) as context:
            inspection.insert()
        self.assertIn("Missing required field(s) for New Inventory", str(context.exception))
        self.assertIn("manufacturer", str(context.exception))
        self.assertIn("key", str(context.exception))

    def test_new_inventory_with_customer_data_fails(self):
        """Test validation failure for 'New Inventory' if customer/pricing fields are populated."""
        inspection = self._create_inspection(
            inspection_type="New Inventory",
            manufacturer="Buffet Crampon",
            model="R13",
            key="B♭",
            wood_type="Grenadilla",
            customer=self.customer.name, # This field should not be here
            preliminary_estimate=500.00
        )
        with self.assertRaises(ValidationError) as context:
            inspection.insert()
        self.assertIn("Customer and pricing fields must be empty", str(context.exception))

    def test_repair_inspection_allows_customer_data(self):
        """Test that 'Repair' type inspections correctly allow customer and estimate fields."""
        inspection = self._create_inspection(
            inspection_type="Repair",
            customer=self.customer.name,
            preliminary_estimate=150.00
        )
        # Should save without error
        inspection.insert()
        self.assertEqual(inspection.customer, self.customer.name)
        self.assertEqual(inspection.preliminary_estimate, 150.00)
    
    # --- On Submit Hook Tests ---

    def test_on_submit_creates_instrument_profile(self):
        """Verify that submitting an inspection creates a new Instrument Profile if one doesn't exist."""
        # Setup: Ensure no profile exists for this new serial
        new_serial_no = "TEST-SN-NEWPROFILE"
        self._create_serial_no(new_serial_no)
        self.assertIsNone(frappe.db.exists("Instrument Profile", {"instrument": new_serial_no}))

        # Create and submit the inspection
        inspection = self._create_inspection(
            serial_no=new_serial_no,
            inspection_type="New Inventory",
            manufacturer="Selmer", model="Presence", key="A", wood_type="Grenadilla",
            body_material="Grenadilla Wood",
            key_plating="Silver",
            current_status="For Sale",
            customer=None
        )
        inspection.insert()
        inspection.submit()
        
        self.assertEqual(inspection.docstatus, 1) # Submitted

        # Verification
        profile = frappe.get_doc("Instrument Profile", {"instrument": new_serial_no})
        self.assertIsNotNone(profile)
        self.assertEqual(profile.instrument, new_serial_no)
        self.assertEqual(profile.body_material, "Grenadilla Wood")
        self.assertEqual(profile.key_plating, "Silver")
        self.assertEqual(profile.current_status, "For Sale")

    def test_on_submit_updates_existing_instrument_profile(self):
        """Verify that submitting an inspection updates an existing Instrument Profile."""
        # Setup: Create an existing profile
        existing_serial_no = "TEST-SN-UPDATE"
        self._create_serial_no(existing_serial_no)
        
        # Create an initial Instrument Profile to be updated
        # This part requires knowledge of the Instrument Profile DocType's fields
        # Creating a dummy DocType for the test
        if not frappe.db.exists("DocType", "Instrument Profile"):
            frappe.get_doc({
                "doctype": "DocType", "name": "Instrument Profile", "module": "Core", "custom": 1,
                "fields": [
                    {"fieldname": "instrument", "fieldtype": "Link", "options": "Serial No"},
                    {"fieldname": "body_material", "fieldtype": "Data"},
                    {"fieldname": "key_plating", "fieldtype": "Data"},
                    {"fieldname": "current_status", "fieldtype": "Data"},
                    {"fieldname": "bore_style", "fieldtype": "Data"},
                    {"fieldname": "bore_measurement", "fieldtype": "Float"},
                    {"fieldname": "key_system", "fieldtype": "Data"},
                    {"fieldname": "number_of_keys_rings", "fieldtype": "Data"},
                    {"fieldname": "pad_type_current", "fieldtype": "Data"},
                    {"fieldname": "pitch_standard", "fieldtype": "Data"},
                    {"fieldname": "profile_image", "fieldtype": "Attach Image"},
                    {"fieldname": "spring_type", "fieldtype": "Data"},
                    {"fieldname": "thumb_rest", "fieldtype": "Data"},
                    {"fieldname": "tone_hole_style", "fieldtype": "Data"},
                    {"fieldname": "current_location", "fieldtype": "Data"}
                ]
            }).insert()

        initial_profile = frappe.get_doc({
            "doctype": "Instrument Profile",
            "instrument": existing_serial_no,
            "body_material": "Old Material",
            "key_plating": "Nickel",
            "current_status": "In Workshop"
        }).insert()

        # Create and submit the inspection with updated data
        inspection = self._create_inspection(
            serial_no=existing_serial_no,
            inspection_type="QA",
            customer=self.customer.name,
            body_material="Updated Grenadilla",
            key_plating="Silver",
            current_status="For Sale"
        )
        inspection.insert()
        inspection.submit()
        
        # Verification
        updated_profile = frappe.get_doc("Instrument Profile", initial_profile.name)
        self.assertEqual(updated_profile.body_material, "Updated Grenadilla")
        self.assertEqual(updated_profile.key_plating, "Silver")
        self.assertEqual(updated_profile.current_status, "For Sale")
        self.assertEqual(frappe.db.count("Instrument Profile", {"instrument": existing_serial_no}), 1) # Ensure no new profile was made

    # --- Child Table Tests ---
    
    def test_child_table_data_persistence(self):
        """Test if data added to a child table is correctly saved."""
        inspection = self._create_inspection()
        
        # This test assumes the 'Inspection Finding' DocType has at least these fields.
        # Create a dummy DocType for the child table if it doesn't exist.
        if not frappe.db.exists("DocType", "Inspection Finding"):
            frappe.get_doc({
                "doctype": "DocType", "name": "Inspection Finding", "module": "Core", "custom": 1, "istable": 1,
                "fields": [
                    {"fieldname": "area", "fieldtype": "Data"},
                    {"fieldname": "observation", "fieldtype": "Small Text"},
                    {"fieldname": "recommendation", "fieldtype": "Small Text"},
                ]
            }).insert()
            
        inspection.append("visual_inspection", {
            "area": "Upper Joint",
            "observation": "Minor scratch near trill keys.",
            "recommendation": "Buff and polish."
        })
        
        inspection.insert()
        
        # Fetch the document from the DB to verify
        saved_doc = frappe.get_doc("Instrument Inspection", inspection.name)
        self.assertEqual(len(saved_doc.visual_inspection), 1)
        self.assertEqual(saved_doc.visual_inspection[0].area, "Upper Joint")
        self.assertEqual(saved_doc.visual_inspection[0].recommendation, "Buff and polish.")


if __name__ == '__main__':
    # This allows running the tests directly from the command line
    # For Frappe, it's typically run via `bench --site [site_name] test [app_name]`
    unittest.main()

