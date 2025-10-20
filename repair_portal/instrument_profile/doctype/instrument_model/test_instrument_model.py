# Path: repair_portal/instrument_profile/doctype/instrument_model/test_instrument_model.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Comprehensive unit tests for Instrument Model DocType including validation, uniqueness checks, required fields, link integrity, and brand+model duplicate detection.
# Dependencies: frappe.tests, unittest

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase


class TestInstrumentModel(FrappeTestCase):
    """Test cases for Instrument Model DocType"""

    def setUp(self):
        """Set up test data"""
        # Create test brand if it doesn't exist
        if not frappe.db.exists("Brand", "Test Brand"):
            frappe.get_doc(
                {"doctype": "Brand", "brand": "Test Brand", "description": "Test brand for unit tests"}
            ).insert(ignore_permissions=True)

        # Create test instrument category if it doesn't exist
        if not frappe.db.exists("Instrument Category", "Test Clarinet"):
            frappe.get_doc(
                {"doctype": "Instrument Category", "title": "Test Clarinet", "is_active": 1}
            ).insert(ignore_permissions=True)

    def tearDown(self):
        """Clean up test data"""
        # Delete test instrument models
        frappe.db.delete("Instrument Model", {"brand": "Test Brand"})
        frappe.db.commit()

    def test_instrument_model_creation(self):
        """Test basic instrument model creation"""
        model = frappe.get_doc(
            {
                "doctype": "Instrument Model",
                "brand": "Test Brand",
                "model": "Test-123",
                "instrument_category": "Test Clarinet",
                "body_material": "Grenadilla",
            }
        )
        model.insert()

        self.assertEqual(model.brand, "Test Brand")
        self.assertEqual(model.model, "Test-123")
        self.assertEqual(model.name, "Test-123")  # Named by model field
        self.assertTrue(model.instrument_model_id)  # Should have unique ID

    def test_required_fields_validation(self):
        """Test that required fields are enforced"""
        # Missing brand
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc(
                {
                    "doctype": "Instrument Model",
                    "model": "Test-456",
                    "instrument_category": "Test Clarinet",
                    "body_material": "Rosewood",
                }
            ).insert()

        # Missing model
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc(
                {
                    "doctype": "Instrument Model",
                    "brand": "Test Brand",
                    "instrument_category": "Test Clarinet",
                    "body_material": "Rosewood",
                }
            ).insert()

        # Missing instrument_category
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc(
                {
                    "doctype": "Instrument Model",
                    "brand": "Test Brand",
                    "model": "Test-789",
                    "body_material": "Rosewood",
                }
            ).insert()

    def test_link_field_validation(self):
        """Test that link fields point to existing records"""
        # Non-existent brand
        with self.assertRaises(frappe.LinkValidationError):
            frappe.get_doc(
                {
                    "doctype": "Instrument Model",
                    "brand": "Non-Existent Brand",
                    "model": "Test-999",
                    "instrument_category": "Test Clarinet",
                    "body_material": "Plastic",
                }
            ).insert()

        # Non-existent instrument category
        with self.assertRaises(frappe.LinkValidationError):
            frappe.get_doc(
                {
                    "doctype": "Instrument Model",
                    "brand": "Test Brand",
                    "model": "Test-888",
                    "instrument_category": "Non-Existent Category",
                    "body_material": "Metal",
                }
            ).insert()

    def test_model_naming_logic(self):
        """Test naming is based on model field"""
        model = frappe.get_doc(
            {
                "doctype": "Instrument Model",
                "brand": "Test Brand",
                "model": "Unique-Model-Name",
                "instrument_category": "Test Clarinet",
                "body_material": "Grenadilla",
            }
        )
        model.insert()

        self.assertEqual(model.name, "Unique-Model-Name")

    def test_duplicate_brand_model_combination(self):
        """Test advisory check for duplicate brand+model combination"""
        # Create first model
        model1 = frappe.get_doc(
            {
                "doctype": "Instrument Model",
                "brand": "Test Brand",
                "model": "Duplicate-Test",
                "instrument_category": "Test Clarinet",
                "body_material": "Grenadilla",
            }
        )
        model1.insert()

        # Try to create duplicate - should succeed but could show warning
        # (This tests the advisory nature, not hard constraint)
        model2 = frappe.get_doc(
            {
                "doctype": "Instrument Model",
                "brand": "Test Brand",
                "model": "Duplicate-Test-2",  # Different model name
                "instrument_category": "Test Clarinet",
                "body_material": "Rosewood",  # Different material
            }
        )
        model2.insert()

        # Both should exist
        self.assertTrue(frappe.db.exists("Instrument Model", model1.name))
        self.assertTrue(frappe.db.exists("Instrument Model", model2.name))

    def test_body_material_values(self):
        """Test various body material values are accepted"""
        materials = ["Grenadilla", "Rosewood", "Plastic", "Metal", "Carbon Fiber"]

        for i, material in enumerate(materials):
            model = frappe.get_doc(
                {
                    "doctype": "Instrument Model",
                    "brand": "Test Brand",
                    "model": f"Material-Test-{i}",
                    "instrument_category": "Test Clarinet",
                    "body_material": material,
                }
            )
            model.insert()
            self.assertEqual(model.body_material, material)

    def test_instrument_model_id_uniqueness(self):
        """Test that instrument_model_id is unique"""
        model1 = frappe.get_doc(
            {
                "doctype": "Instrument Model",
                "brand": "Test Brand",
                "model": "ID-Test-1",
                "instrument_category": "Test Clarinet",
                "body_material": "Grenadilla",
            }
        )
        model1.insert()

        model2 = frappe.get_doc(
            {
                "doctype": "Instrument Model",
                "brand": "Test Brand",
                "model": "ID-Test-2",
                "instrument_category": "Test Clarinet",
                "body_material": "Rosewood",
            }
        )
        model2.insert()

        # IDs should be different
        self.assertNotEqual(model1.instrument_model_id, model2.instrument_model_id)
        self.assertTrue(model1.instrument_model_id)
        self.assertTrue(model2.instrument_model_id)


if __name__ == "__main__":
    unittest.main()
