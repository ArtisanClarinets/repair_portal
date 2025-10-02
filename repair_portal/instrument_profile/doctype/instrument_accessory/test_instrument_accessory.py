# Path: repair_portal/instrument_profile/doctype/instrument_accessory/test_instrument_accessory.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Comprehensive unit tests for Instrument Accessory DocType including validation, link integrity, quantity validation, and accessory-instrument relationships.
# Dependencies: frappe.tests, unittest

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase


class TestInstrumentAccessory(FrappeTestCase):
    """Test cases for Instrument Accessory DocType"""
    
    def setUp(self):
        """Set up test data"""
        # Create test brand
        if not frappe.db.exists("Brand", "Test Brand"):
            frappe.get_doc({
                "doctype": "Brand",
                "brand": "Test Brand"
            }).insert(ignore_permissions=True)
        
        # Create test instrument category
        if not frappe.db.exists("Instrument Category", "Test Clarinet"):
            frappe.get_doc({
                "doctype": "Instrument Category",
                "title": "Test Clarinet",
                "is_active": 1
            }).insert(ignore_permissions=True)
        
        # Create test instrument model
        if not frappe.db.exists("Instrument Model", "Test-123"):
            frappe.get_doc({
                "doctype": "Instrument Model",
                "brand": "Test Brand",
                "model": "Test-123",
                "instrument_category": "Test Clarinet",
                "body_material": "Grenadilla"
            }).insert(ignore_permissions=True)
        
        # Create test instrument
        if not frappe.db.exists("Instrument", "ACC-TEST-001"):
            frappe.get_doc({
                "doctype": "Instrument",
                "serial_number": "ACC-TEST-001",
                "instrument_model": "Test-123",
                "workflow_state": "Active"
            }).insert(ignore_permissions=True)
    
    def tearDown(self):
        """Clean up test data"""
        # Delete test accessories
        frappe.db.delete("Instrument Accessory", {"instrument": "ACC-TEST-001"})
        frappe.db.commit()
    
    def test_instrument_accessory_creation(self):
        """Test basic instrument accessory creation"""
        accessory = frappe.get_doc({
            "doctype": "Instrument Accessory",
            "instrument": "ACC-TEST-001",
            "accessory_type": "Case",
            "description": "Hard case for clarinet",
            "quantity": 1
        })
        accessory.insert()
        
        self.assertEqual(accessory.instrument, "ACC-TEST-001")
        self.assertEqual(accessory.accessory_type, "Case")
        self.assertEqual(accessory.description, "Hard case for clarinet")
        self.assertEqual(accessory.quantity, 1)
    
    def test_required_fields_validation(self):
        """Test that required fields are enforced"""
        # Missing instrument
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc({
                "doctype": "Instrument Accessory",
                "accessory_type": "Case",
                "description": "Test case",
                "quantity": 1
            }).insert()
        
        # Missing accessory_type
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc({
                "doctype": "Instrument Accessory",
                "instrument": "ACC-TEST-001",
                "description": "Test accessory",
                "quantity": 1
            }).insert()
        
        # Missing description
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc({
                "doctype": "Instrument Accessory",
                "instrument": "ACC-TEST-001",
                "accessory_type": "Case",
                "quantity": 1
            }).insert()
    
    def test_link_field_validation(self):
        """Test that instrument link points to existing record"""
        with self.assertRaises(frappe.LinkValidationError):
            frappe.get_doc({
                "doctype": "Instrument Accessory",
                "instrument": "NON-EXISTENT-INSTRUMENT",
                "accessory_type": "Case",
                "description": "Test case",
                "quantity": 1
            }).insert()
    
    def test_accessory_types(self):
        """Test various accessory types"""
        accessory_types = [
            "Case", "Mouthpiece", "Reed", "Ligature", "Cap", 
            "Swab", "Stand", "Music Stand", "Metronome", "Tuner"
        ]
        
        for i, acc_type in enumerate(accessory_types):
            accessory = frappe.get_doc({
                "doctype": "Instrument Accessory",
                "instrument": "ACC-TEST-001",
                "accessory_type": acc_type,
                "description": f"Test {acc_type.lower()}",
                "quantity": 1
            })
            accessory.insert()
            self.assertEqual(accessory.accessory_type, acc_type)
    
    def test_quantity_validation(self):
        """Test quantity field validation"""
        # Positive quantity
        accessory1 = frappe.get_doc({
            "doctype": "Instrument Accessory",
            "instrument": "ACC-TEST-001",
            "accessory_type": "Reed",
            "description": "Box of 10 reeds",
            "quantity": 10
        })
        accessory1.insert()
        self.assertEqual(accessory1.quantity, 10)
        
        # Single quantity
        accessory2 = frappe.get_doc({
            "doctype": "Instrument Accessory",
            "instrument": "ACC-TEST-001",
            "accessory_type": "Case",
            "description": "Single hard case",
            "quantity": 1
        })
        accessory2.insert()
        self.assertEqual(accessory2.quantity, 1)
        
        # Large quantity
        accessory3 = frappe.get_doc({
            "doctype": "Instrument Accessory",
            "instrument": "ACC-TEST-001",
            "accessory_type": "Reed",
            "description": "Large reed supply",
            "quantity": 100
        })
        accessory3.insert()
        self.assertEqual(accessory3.quantity, 100)
    
    def test_description_content(self):
        """Test description field content"""
        # Short description
        accessory1 = frappe.get_doc({
            "doctype": "Instrument Accessory",
            "instrument": "ACC-TEST-001",
            "accessory_type": "Cap",
            "description": "Mouthpiece cap",
            "quantity": 1
        })
        accessory1.insert()
        self.assertEqual(accessory1.description, "Mouthpiece cap")
        
        # Detailed description
        detailed_desc = "Professional grade hard case with foam padding, humidity control, compartments for accessories, and locking mechanism"
        accessory2 = frappe.get_doc({
            "doctype": "Instrument Accessory",
            "instrument": "ACC-TEST-001",
            "accessory_type": "Case",
            "description": detailed_desc,
            "quantity": 1
        })
        accessory2.insert()
        self.assertEqual(accessory2.description, detailed_desc)
    
    def test_optional_fields(self):
        """Test optional fields can be set"""
        accessory = frappe.get_doc({
            "doctype": "Instrument Accessory",
            "instrument": "ACC-TEST-001",
            "accessory_type": "Mouthpiece",
            "description": "Professional mouthpiece",
            "quantity": 1,
            "brand": "Vandoren",
            "model": "M30",
            "serial_number": "MP-12345",
            "purchase_date": "2023-01-15",
            "cost": 150.00,
            "condition": "New",
            "notes": "Purchased for professional performances"
        })
        accessory.insert()
        
        self.assertEqual(accessory.brand, "Vandoren")
        self.assertEqual(accessory.model, "M30")
        self.assertEqual(accessory.serial_number, "MP-12345")
        self.assertEqual(str(accessory.purchase_date), "2023-01-15")
        self.assertEqual(float(accessory.cost), 150.00)
        self.assertEqual(accessory.condition, "New")
        self.assertEqual(accessory.notes, "Purchased for professional performances")
    
    def test_condition_values(self):
        """Test various condition values"""
        conditions = ["New", "Excellent", "Good", "Fair", "Poor", "Needs Replacement"]
        
        for i, condition in enumerate(conditions):
            accessory = frappe.get_doc({
                "doctype": "Instrument Accessory",
                "instrument": "ACC-TEST-001",
                "accessory_type": "Reed",
                "description": f"Reed in {condition.lower()} condition",
                "quantity": 1,
                "condition": condition
            })
            accessory.insert()
            self.assertEqual(accessory.condition, condition)
    
    def test_multiple_accessories_per_instrument(self):
        """Test that multiple accessories can be associated with one instrument"""
        accessories_data = [
            {"type": "Case", "desc": "Hard case", "qty": 1},
            {"type": "Mouthpiece", "desc": "Performance mouthpiece", "qty": 1},
            {"type": "Reed", "desc": "Reed box", "qty": 10},
            {"type": "Swab", "desc": "Cleaning swab", "qty": 2}
        ]
        
        created_accessories = []
        for acc_data in accessories_data:
            accessory = frappe.get_doc({
                "doctype": "Instrument Accessory",
                "instrument": "ACC-TEST-001",
                "accessory_type": acc_data["type"],
                "description": acc_data["desc"],
                "quantity": acc_data["qty"]
            })
            accessory.insert()
            created_accessories.append(accessory)
        
        # All accessories should be created successfully
        self.assertEqual(len(created_accessories), 4)
        for accessory in created_accessories:
            self.assertEqual(accessory.instrument, "ACC-TEST-001")
    
    def test_cost_validation(self):
        """Test cost field validation"""
        # Valid cost
        accessory1 = frappe.get_doc({
            "doctype": "Instrument Accessory",
            "instrument": "ACC-TEST-001",
            "accessory_type": "Case",
            "description": "Expensive case",
            "quantity": 1,
            "cost": 299.99
        })
        accessory1.insert()
        self.assertEqual(float(accessory1.cost), 299.99)
        
        # Zero cost (free/included)
        accessory2 = frappe.get_doc({
            "doctype": "Instrument Accessory",
            "instrument": "ACC-TEST-001",
            "accessory_type": "Swab",
            "description": "Included swab",
            "quantity": 1,
            "cost": 0.00
        })
        accessory2.insert()
        self.assertEqual(float(accessory2.cost), 0.00)
    
    def test_date_validation(self):
        """Test date field validation"""
        accessory = frappe.get_doc({
            "doctype": "Instrument Accessory",
            "instrument": "ACC-TEST-001",
            "accessory_type": "Mouthpiece",
            "description": "Date test mouthpiece",
            "quantity": 1,
            "purchase_date": "2023-06-15"
        })
        accessory.insert()
        
        self.assertEqual(str(accessory.purchase_date), "2023-06-15")


if __name__ == "__main__":
    unittest.main()