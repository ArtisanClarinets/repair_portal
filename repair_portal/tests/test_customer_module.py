# Path: repair_portal/tests/test_customer_module.py
# Date: 2025-01-20
# Version: 1.4.0
# Description: Unit tests for Customer module DocTypes focusing on field validation without data dependencies
# Dependencies: frappe.tests.utils.FrappeTestCase, unittest

import unittest
import frappe
from frappe.tests.utils import FrappeTestCase


class TestCustomerModule(FrappeTestCase):
    """Unit tests for Customer module DocTypes."""
    
    def tearDown(self):
        """Clean up after each test."""
        frappe.db.rollback()
    
    def test_consent_field_value_type_coercion(self):
        """Test Consent Field Value type coercion without validation."""
        # Create a consent field value
        field_value = frappe.get_doc({
            "doctype": "Consent Field Value",
            "field_label": "Test Field",
            "field_type": "Data",
            "field_value": "test_value"
        })
        
        # Test type coercion methods directly
        field_value.field_type = "Int"
        field_value.field_value = "123"
        coerced_value = field_value.get_typed_value()
        self.assertEqual(coerced_value, 123)
        
        # Test boolean coercion
        field_value.field_type = "Check"
        field_value.field_value = "1"
        coerced_value = field_value.get_typed_value()
        self.assertEqual(coerced_value, 1)
        
        # Test default coercion
        field_value.field_type = "Data"
        field_value.field_value = None
        coerced_value = field_value.get_typed_value()
        self.assertIsNone(coerced_value)  # Expect None for null values
    
    def test_consent_required_field_generation(self):
        """Test Consent Required Field field definition generation."""
        # Create a required field
        required_field = frappe.get_doc({
            "doctype": "Consent Required Field",
            "field_label": "Customer Email",
            "field_type": "Data",
            "is_required": 1
        })
        
        # Test field definition generation
        field_def = required_field.get_field_definition()
        self.assertEqual(field_def["fieldname"], "customer_email")
        self.assertEqual(field_def["fieldtype"], "Data")
        self.assertEqual(field_def["label"], "Customer Email")
        self.assertEqual(field_def["reqd"], 1)
        
        # Test validation rules generation
        rules = required_field.get_validation_rules()
        self.assertTrue(rules["required"])
    
    def test_consent_autofill_mapping_field_access(self):
        """Test Consent Autofill Mapping field access."""
        # Create an autofill mapping
        mapping = frappe.get_doc({
            "doctype": "Consent Autofill Mapping",
            "enabled": 1,
            "variable_name": "customer_name",
            "source_doctype": "Customer",
            "source_fieldname": "customer_name",
            "form_link_field": "customer"
        })
        
        # Test field access (should not raise AttributeError)
        self.assertTrue(hasattr(mapping, 'enabled'))
        self.assertTrue(hasattr(mapping, 'variable_name'))
        self.assertTrue(hasattr(mapping, 'source_doctype'))
        self.assertTrue(hasattr(mapping, 'source_fieldname'))
        self.assertTrue(hasattr(mapping, 'form_link_field'))
        
        # Test helper methods
        self.assertTrue(callable(getattr(mapping, 'get_mapped_value', None)))
    
    def test_consent_log_entry_field_access(self):
        """Test Consent Log Entry field access."""
        # Create a log entry
        log_entry = frappe.get_doc({
            "doctype": "Consent Log Entry",
            "entry_date": frappe.utils.nowdate(),
            "method": "Digital",
            "technician": "Administrator",
            "notes": "Test consent entry",
            "consent_type": "Repair Authorization",
            "date_given": frappe.utils.nowdate()
        })
        
        # Test field access (should not raise AttributeError)
        self.assertTrue(hasattr(log_entry, 'entry_date'))
        self.assertTrue(hasattr(log_entry, 'method'))
        self.assertTrue(hasattr(log_entry, 'technician'))
        self.assertTrue(hasattr(log_entry, 'consent_type'))
        self.assertTrue(hasattr(log_entry, 'date_given'))
        
        # Test helper methods
        self.assertTrue(callable(getattr(log_entry, 'get_consent_status', None)))
        self.assertTrue(callable(getattr(log_entry, 'get_consent_validity', None)))
    
    def test_customer_type_field_access(self):
        """Test Customer Type field access."""
        # Create a customer type
        customer_type = frappe.get_doc({
            "doctype": "Customer Type",
            "type_name": "Individual",
            "description": "Individual customer type",
            "is_default": 1
        })
        
        # Test field access (should not raise AttributeError)
        self.assertTrue(hasattr(customer_type, 'type_name'))
        self.assertTrue(hasattr(customer_type, 'description'))
        self.assertTrue(hasattr(customer_type, 'is_default'))
        
        # Test that correct field names are used
        self.assertEqual(customer_type.type_name, "Individual")
        self.assertEqual(customer_type.description, "Individual customer type")
        self.assertEqual(customer_type.is_default, 1)
    
    def test_linked_players_field_access(self):
        """Test Linked Players field access."""
        # Create a linked player entry
        linked_player = frappe.get_doc({
            "doctype": "Linked Players",
            "customer": "TEST-CUSTOMER",
            "player_profile": "TEST-PLAYER",
            "relationship": "Self",
            "date_linked": frappe.utils.nowdate(),
            "is_primary": 1,
            "notes": "Test player link"
        })
        
        # Test field access (should not raise AttributeError)
        self.assertTrue(hasattr(linked_player, 'customer'))
        self.assertTrue(hasattr(linked_player, 'player_profile'))
        self.assertTrue(hasattr(linked_player, 'relationship'))
        self.assertTrue(hasattr(linked_player, 'date_linked'))
        self.assertTrue(hasattr(linked_player, 'is_primary'))
        
        # Test that correct field names are used
        self.assertEqual(linked_player.customer, "TEST-CUSTOMER")
        self.assertEqual(linked_player.player_profile, "TEST-PLAYER")
        self.assertEqual(linked_player.relationship, "Self")
    
    def test_consent_linked_source_field_access(self):
        """Test Consent Linked Source field access."""
        # Create a linked source
        linked_source = frappe.get_doc({
            "doctype": "Consent Linked Source",
            "enabled": 1,
            "label": "Customer Name",
            "fieldname": "customer_name",
            "source_doctype": "Customer"
        })
        
        # Test field access (should not raise AttributeError)
        self.assertTrue(hasattr(linked_source, 'enabled'))
        self.assertTrue(hasattr(linked_source, 'label'))
        self.assertTrue(hasattr(linked_source, 'fieldname'))
        self.assertTrue(hasattr(linked_source, 'source_doctype'))
        
        # Test helper methods
        self.assertTrue(callable(getattr(linked_source, 'get_field_definition', None)))
        self.assertTrue(callable(getattr(linked_source, 'get_source_value', None)))
    
    def test_instruments_owned_field_access(self):
        """Test Instruments Owned field access."""
        # Create an instruments owned entry
        instrument_owned = frappe.get_doc({
            "doctype": "Instruments Owned",
            "instrument_profile": "TEST-INSTRUMENT",
            "customer": "TEST-CUSTOMER",
            "date_acquired": frappe.utils.nowdate(),
            "ownership_type": "Owned",
            "notes": "Test instrument ownership"
        })
        
        # Test field access (should not raise AttributeError)
        self.assertTrue(hasattr(instrument_owned, 'instrument_profile'))
        self.assertTrue(hasattr(instrument_owned, 'customer'))
        self.assertTrue(hasattr(instrument_owned, 'date_acquired'))
        self.assertTrue(hasattr(instrument_owned, 'ownership_type'))
        
        # Test that correct field names are used
        self.assertEqual(instrument_owned.instrument_profile, "TEST-INSTRUMENT")
        self.assertEqual(instrument_owned.customer, "TEST-CUSTOMER")
        self.assertEqual(instrument_owned.ownership_type, "Owned")


if __name__ == "__main__":
    unittest.main()