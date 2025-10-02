# Path: repair_portal/instrument_profile/doctype/instrument_category/test_instrument_category.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Comprehensive unit tests for Instrument Category DocType including validation, uniqueness checks, required fields, and active/inactive state management.
# Dependencies: frappe.tests, unittest

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase


class TestInstrumentCategory(FrappeTestCase):
    """Test cases for Instrument Category DocType"""
    
    def tearDown(self):
        """Clean up test data"""
        # Delete test categories
        frappe.db.delete("Instrument Category", {"title": ["like", "Test Category%"]})
        frappe.db.commit()
    
    def test_instrument_category_creation(self):
        """Test basic instrument category creation"""
        category = frappe.get_doc({
            "doctype": "Instrument Category",
            "title": "Test Category 1",
            "is_active": 1
        })
        category.insert()
        
        self.assertEqual(category.title, "Test Category 1")
        self.assertEqual(category.is_active, 1)
        self.assertTrue(category.name)  # Should have a name
    
    def test_required_field_validation(self):
        """Test that title field is required"""
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc({
                "doctype": "Instrument Category",
                "is_active": 1
            }).insert()
    
    def test_is_active_default_value(self):
        """Test that is_active defaults to 1"""
        category = frappe.get_doc({
            "doctype": "Instrument Category",
            "title": "Test Category 2"
        })
        category.insert()
        
        self.assertEqual(category.is_active, 1)  # Should default to active
    
    def test_inactive_category_creation(self):
        """Test creating inactive category"""
        category = frappe.get_doc({
            "doctype": "Instrument Category",
            "title": "Test Category Inactive",
            "is_active": 0
        })
        category.insert()
        
        self.assertEqual(category.is_active, 0)
    
    def test_category_naming(self):
        """Test that category naming works correctly"""
        category = frappe.get_doc({
            "doctype": "Instrument Category",
            "title": "Test Category Unique Name",
            "is_active": 1
        })
        category.insert()
        
        # Name should be auto-generated
        self.assertTrue(category.name)
        self.assertNotEqual(category.name, category.title)  # Name != title
    
    def test_title_uniqueness(self):
        """Test that titles can be duplicated (no unique constraint)"""
        # Create first category
        category1 = frappe.get_doc({
            "doctype": "Instrument Category",
            "title": "Duplicate Title Test",
            "is_active": 1
        })
        category1.insert()
        
        # Create second category with same title - should work
        category2 = frappe.get_doc({
            "doctype": "Instrument Category",
            "title": "Duplicate Title Test",
            "is_active": 0
        })
        category2.insert()
        
        # Both should exist
        self.assertTrue(frappe.db.exists("Instrument Category", category1.name))
        self.assertTrue(frappe.db.exists("Instrument Category", category2.name))
        self.assertNotEqual(category1.name, category2.name)
    
    def test_title_validation(self):
        """Test title content validation"""
        # Empty title should fail
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc({
                "doctype": "Instrument Category",
                "title": "",
                "is_active": 1
            }).insert()
        
        # None title should fail
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc({
                "doctype": "Instrument Category",
                "title": None,
                "is_active": 1
            }).insert()
    
    def test_category_state_changes(self):
        """Test changing active state"""
        category = frappe.get_doc({
            "doctype": "Instrument Category",
            "title": "Test Category State Change",
            "is_active": 1
        })
        category.insert()
        
        # Change to inactive
        category.is_active = 0
        category.save()
        
        # Reload and check
        category.reload()
        self.assertEqual(category.is_active, 0)
        
        # Change back to active
        category.is_active = 1
        category.save()
        
        category.reload()
        self.assertEqual(category.is_active, 1)
    
    def test_various_title_formats(self):
        """Test various title formats are accepted"""
        titles = [
            "Clarinet",
            "Bass Clarinet",
            "A Clarinet",
            "Eb Clarinet",
            "Contrabass Clarinet",
            "Piccolo Clarinet",
            "Alto Clarinet"
        ]
        
        for i, title in enumerate(titles):
            category = frappe.get_doc({
                "doctype": "Instrument Category",
                "title": f"{title} Test {i}",
                "is_active": 1
            })
            category.insert()
            self.assertEqual(category.title, f"{title} Test {i}")
    
    def test_long_title_handling(self):
        """Test handling of long titles"""
        long_title = "Very Long Instrument Category Title That Exceeds Normal Length" * 3
        
        category = frappe.get_doc({
            "doctype": "Instrument Category",
            "title": long_title[:140],  # Limit to reasonable length
            "is_active": 1
        })
        category.insert()
        
        self.assertTrue(len(category.title) <= 140)


if __name__ == "__main__":
    unittest.main()