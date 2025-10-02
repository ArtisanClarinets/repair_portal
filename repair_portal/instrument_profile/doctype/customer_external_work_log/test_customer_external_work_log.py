# Path: repair_portal/instrument_profile/doctype/customer_external_work_log/test_customer_external_work_log.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Comprehensive unit tests for Customer External Work Log DocType including validation, link integrity, date validation, cost validation, and workflow state management.
# Dependencies: frappe.tests, unittest

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase
from decimal import Decimal


class TestCustomerExternalWorkLog(FrappeTestCase):
    """Test cases for Customer External Work Log DocType"""
    
    def setUp(self):
        """Set up test data"""
        # Create test customer
        if not frappe.db.exists("Customer", "Test Customer"):
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "Test Customer",
                "customer_type": "Individual"
            }).insert(ignore_permissions=True)
        
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
        if not frappe.db.exists("Instrument", "EXT-WORK-001"):
            frappe.get_doc({
                "doctype": "Instrument",
                "serial_number": "EXT-WORK-001",
                "instrument_model": "Test-123",
                "workflow_state": "Active"
            }).insert(ignore_permissions=True)
    
    def tearDown(self):
        """Clean up test data"""
        # Delete test external work logs
        frappe.db.delete("Customer External Work Log", {"instrument": "EXT-WORK-001"})
        frappe.db.commit()
    
    def test_external_work_log_creation(self):
        """Test basic external work log creation"""
        log = frappe.get_doc({
            "doctype": "Customer External Work Log",
            "customer": "Test Customer",
            "instrument": "EXT-WORK-001",
            "work_date": "2023-01-15",
            "work_description": "External repair work",
            "cost": 150.00,
            "workflow_state": "Draft"
        })
        log.insert()
        
        self.assertEqual(log.customer, "Test Customer")
        self.assertEqual(log.instrument, "EXT-WORK-001")
        self.assertEqual(str(log.work_date), "2023-01-15")
        self.assertEqual(log.work_description, "External repair work")
        self.assertEqual(float(log.cost), 150.00)
        self.assertEqual(log.workflow_state, "Draft")
    
    def test_required_fields_validation(self):
        """Test that required fields are enforced"""
        # Missing customer
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc({
                "doctype": "Customer External Work Log",
                "instrument": "EXT-WORK-001",
                "work_date": "2023-01-15",
                "work_description": "Test work",
                "cost": 100.00,
                "workflow_state": "Draft"
            }).insert()
        
        # Missing instrument
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc({
                "doctype": "Customer External Work Log",
                "customer": "Test Customer",
                "work_date": "2023-01-15",
                "work_description": "Test work",
                "cost": 100.00,
                "workflow_state": "Draft"
            }).insert()
        
        # Missing work_date
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc({
                "doctype": "Customer External Work Log",
                "customer": "Test Customer",
                "instrument": "EXT-WORK-001",
                "work_description": "Test work",
                "cost": 100.00,
                "workflow_state": "Draft"
            }).insert()
        
        # Missing work_description
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc({
                "doctype": "Customer External Work Log",
                "customer": "Test Customer",
                "instrument": "EXT-WORK-001",
                "work_date": "2023-01-15",
                "cost": 100.00,
                "workflow_state": "Draft"
            }).insert()
    
    def test_link_field_validation(self):
        """Test that link fields point to existing records"""
        # Non-existent customer
        with self.assertRaises(frappe.LinkValidationError):
            frappe.get_doc({
                "doctype": "Customer External Work Log",
                "customer": "Non-Existent Customer",
                "instrument": "EXT-WORK-001",
                "work_date": "2023-01-15",
                "work_description": "Test work",
                "cost": 100.00,
                "workflow_state": "Draft"
            }).insert()
        
        # Non-existent instrument
        with self.assertRaises(frappe.LinkValidationError):
            frappe.get_doc({
                "doctype": "Customer External Work Log",
                "customer": "Test Customer",
                "instrument": "NON-EXISTENT-SERIAL",
                "work_date": "2023-01-15",
                "work_description": "Test work",
                "cost": 100.00,
                "workflow_state": "Draft"
            }).insert()
    
    def test_cost_validation(self):
        """Test cost field validation"""
        # Valid positive cost
        log1 = frappe.get_doc({
            "doctype": "Customer External Work Log",
            "customer": "Test Customer",
            "instrument": "EXT-WORK-001",
            "work_date": "2023-01-15",
            "work_description": "Positive cost work",
            "cost": 250.50,
            "workflow_state": "Draft"
        })
        log1.insert()
        self.assertEqual(float(log1.cost), 250.50)
        
        # Zero cost (should be allowed)
        log2 = frappe.get_doc({
            "doctype": "Customer External Work Log",
            "customer": "Test Customer",
            "instrument": "EXT-WORK-001",
            "work_date": "2023-01-16",
            "work_description": "Free warranty work",
            "cost": 0.00,
            "workflow_state": "Draft"
        })
        log2.insert()
        self.assertEqual(float(log2.cost), 0.00)
        
        # Test precision
        log3 = frappe.get_doc({
            "doctype": "Customer External Work Log",
            "customer": "Test Customer",
            "instrument": "EXT-WORK-001",
            "work_date": "2023-01-17",
            "work_description": "Precise cost work",
            "cost": 123.45,
            "workflow_state": "Draft"
        })
        log3.insert()
        self.assertEqual(float(log3.cost), 123.45)
    
    def test_workflow_state_values(self):
        """Test valid workflow state values"""
        valid_states = ["Draft", "Verified", "Approved", "Rejected"]
        
        for i, state in enumerate(valid_states):
            log = frappe.get_doc({
                "doctype": "Customer External Work Log",
                "customer": "Test Customer",
                "instrument": "EXT-WORK-001",
                "work_date": f"2023-01-{str(i+20).zfill(2)}",
                "work_description": f"Work for {state} state",
                "cost": (i + 1) * 50.00,
                "workflow_state": state
            })
            log.insert()
            self.assertEqual(log.workflow_state, state)
    
    def test_date_validation(self):
        """Test date field validation"""
        # Valid date
        log = frappe.get_doc({
            "doctype": "Customer External Work Log",
            "customer": "Test Customer",
            "instrument": "EXT-WORK-001",
            "work_date": "2023-06-15",
            "work_description": "Mid-year work",
            "cost": 175.00,
            "workflow_state": "Draft"
        })
        log.insert()
        self.assertEqual(str(log.work_date), "2023-06-15")
        
        # Future date (should be allowed for scheduling)
        log2 = frappe.get_doc({
            "doctype": "Customer External Work Log",
            "customer": "Test Customer",
            "instrument": "EXT-WORK-001",
            "work_date": "2024-01-01",
            "work_description": "Future scheduled work",
            "cost": 200.00,
            "workflow_state": "Draft"
        })
        log2.insert()
        self.assertEqual(str(log2.work_date), "2024-01-01")
    
    def test_work_description_validation(self):
        """Test work description content"""
        # Short description
        log1 = frappe.get_doc({
            "doctype": "Customer External Work Log",
            "customer": "Test Customer",
            "instrument": "EXT-WORK-001",
            "work_date": "2023-02-01",
            "work_description": "Repair",
            "cost": 100.00,
            "workflow_state": "Draft"
        })
        log1.insert()
        self.assertEqual(log1.work_description, "Repair")
        
        # Detailed description
        detailed_desc = "Comprehensive overhaul including pad replacement, spring adjustment, key alignment, and general maintenance performed by certified technician."
        log2 = frappe.get_doc({
            "doctype": "Customer External Work Log",
            "customer": "Test Customer",
            "instrument": "EXT-WORK-001",
            "work_date": "2023-02-02",
            "work_description": detailed_desc,
            "cost": 300.00,
            "workflow_state": "Draft"
        })
        log2.insert()
        self.assertEqual(log2.work_description, detailed_desc)
    
    def test_optional_fields(self):
        """Test optional fields can be set"""
        log = frappe.get_doc({
            "doctype": "Customer External Work Log",
            "customer": "Test Customer",
            "instrument": "EXT-WORK-001",
            "work_date": "2023-03-01",
            "work_description": "Complete service",
            "cost": 225.00,
            "workflow_state": "Verified",
            "service_provider": "ABC Repair Shop",
            "invoice_number": "INV-2023-001",
            "notes": "Excellent work quality"
        })
        log.insert()
        
        self.assertEqual(log.service_provider, "ABC Repair Shop")
        self.assertEqual(log.invoice_number, "INV-2023-001")
        self.assertEqual(log.notes, "Excellent work quality")
    
    def test_workflow_state_transitions(self):
        """Test workflow state changes"""
        log = frappe.get_doc({
            "doctype": "Customer External Work Log",
            "customer": "Test Customer",
            "instrument": "EXT-WORK-001",
            "work_date": "2023-04-01",
            "work_description": "Transition test work",
            "cost": 150.00,
            "workflow_state": "Draft"
        })
        log.insert()
        
        # Change to Verified
        log.workflow_state = "Verified"
        log.save()
        log.reload()
        self.assertEqual(log.workflow_state, "Verified")
        
        # Change to Approved
        log.workflow_state = "Approved"
        log.save()
        log.reload()
        self.assertEqual(log.workflow_state, "Approved")
    
    def test_naming_and_indexing(self):
        """Test that records can be created and retrieved efficiently"""
        log = frappe.get_doc({
            "doctype": "Customer External Work Log",
            "customer": "Test Customer",
            "instrument": "EXT-WORK-001",
            "work_date": "2023-05-01",
            "work_description": "Naming test work",
            "cost": 180.00,
            "workflow_state": "Draft"
        })
        log.insert()
        
        # Should be able to retrieve by name
        retrieved = frappe.get_doc("Customer External Work Log", log.name)
        self.assertEqual(retrieved.customer, "Test Customer")
        self.assertEqual(retrieved.instrument, "EXT-WORK-001")


if __name__ == "__main__":
    unittest.main()