# Path: repair_portal/instrument_profile/doctype/customer_external_work_log/test_customer_external_work_log.py
# Date: 2025-10-02
# Version: 2.0.0
# Description: Comprehensive unit tests for Customer External Work Log DocType including validation, notification logic, and schema compliance.
# Dependencies: frappe.tests, unittest

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase
from unittest.mock import MagicMock, patch

class TestCustomerExternalWorkLog(FrappeTestCase):
    """Test cases for Customer External Work Log DocType"""

    def setUp(self):
        """Set up test data"""
        # Create test customer if not exists (parent)
        if not frappe.db.exists("Customer", "Test Customer"):
            frappe.get_doc(
                {"doctype": "Customer", "customer_name": "Test Customer", "customer_type": "Individual"}
            ).insert(ignore_permissions=True)

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

        # Create test instrument
        if not frappe.db.exists("Instrument", "EXT-WORK-001"):
            frappe.get_doc(
                {
                    "doctype": "Instrument",
                    "serial_number": "EXT-WORK-001",
                    "instrument_model": "Test-123",
                    "workflow_state": "Active",
                }
            ).insert(ignore_permissions=True)

    def tearDown(self):
        """Clean up test data"""
        pass

    def test_external_work_log_creation(self):
        """Test basic external work log creation"""
        # It's a child table, usually created within a parent.
        # But we can test creating it as a standalone doc if we provide parent fields?
        # Typically child tables are tested via parent.
        # However, we can use frappe.get_doc with child table doctype for validation logic testing.

        log = frappe.get_doc(
            {
                "doctype": "Customer External Work Log",
                "instrument": "EXT-WORK-001",
                "service_date": "2023-01-15",
                "service_type": "Repair",
                "service_notes": "External repair work",
                "external_shop_name": "Best Repair Shop",
                "parent": "Test Customer",
                "parenttype": "Customer",
                "parentfield": "external_work_logs"
            }
        )
        # We don't insert because it's a child table and parent linkage might fail if parent structure isn't perfect.
        # But we can call validate()
        log.validate()

        self.assertEqual(log.instrument, "EXT-WORK-001")
        self.assertEqual(str(log.service_date), "2023-01-15")
        self.assertEqual(log.service_type, "Repair")
        self.assertEqual(log.service_notes, "External repair work")
        self.assertEqual(log.external_shop_name, "Best Repair Shop")

    def test_required_fields_validation(self):
        """Test that required fields are enforced"""
        # Missing service_type
        log = frappe.get_doc({
            "doctype": "Customer External Work Log",
            "instrument": "EXT-WORK-001",
            "service_date": "2023-01-15",
            "external_shop_name": "Shop",
        })
        from repair_portal.instrument_profile.utils.input_validation import ValidationError
        with self.assertRaises((frappe.MandatoryError, ValidationError)):
            log.validate()

    def test_notification_logic_mocked(self):
        """Test notification logic using mocks (unit test style)"""
        # This test mocks frappe.get_all and frappe.get_doc to verify logic without DB

        # Mocking logic similar to reproduce_notification_logic.py
        with patch('frappe.get_all') as mock_get_all, \
             patch('frappe.get_doc') as mock_get_doc:

            # Setup mock returns
            def get_all_side_effect(doctype, filters=None, pluck=None):
                if doctype == "Has Role":
                    if filters["role"] == "Repair Manager":
                        return ["manager@example.com"]
                    if filters["role"] == "Technician":
                        return ["tech@example.com"]
                if doctype == "User":
                    return filters["name"][1]
                return []
            mock_get_all.side_effect = get_all_side_effect

            mock_notification = MagicMock()
            mock_get_doc.return_value = mock_notification

            # Create doc instance
            log = frappe.get_doc({
                "doctype": "Customer External Work Log",
                "service_type": "Repair",
                "service_date": "2023-01-01",
                "external_shop_name": "Test Shop",
                "parent": "Cust-001",
                "parenttype": "Customer"
            })

            # Call notification method
            log._send_notifications()

            # Verify results
            # Repair Manager should be prioritized
            call_args_list = mock_get_doc.call_args_list
            recipients = [call.args[0]["for_user"] for call in call_args_list]

            self.assertIn("manager@example.com", recipients)
            self.assertNotIn("tech@example.com", recipients)
            self.assertNotIn("Administrator", recipients)

    def test_notification_logic_technician_fallback(self):
        """Test notification logic fallback to technician"""
        with patch('frappe.get_all') as mock_get_all, \
             patch('frappe.get_doc') as mock_get_doc:

            def get_all_side_effect(doctype, filters=None, pluck=None):
                if doctype == "Has Role":
                    if filters["role"] == "Repair Manager":
                        return [] # No managers
                    if filters["role"] == "Technician":
                        return ["tech@example.com"]
                if doctype == "User":
                    return filters["name"][1]
                return []
            mock_get_all.side_effect = get_all_side_effect

            mock_notification = MagicMock()
            mock_get_doc.return_value = mock_notification

            log = frappe.get_doc({
                "doctype": "Customer External Work Log",
                "service_type": "Repair",
                "service_date": "2023-01-01",
                "external_shop_name": "Test Shop",
                "parent": "Cust-001",
                "parenttype": "Customer"
            })

            log._send_notifications()

            call_args_list = mock_get_doc.call_args_list
            recipients = [call.args[0]["for_user"] for call in call_args_list]

            self.assertIn("tech@example.com", recipients)
            self.assertNotIn("manager@example.com", recipients)
