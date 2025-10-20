# Path: repair_portal/repair_logging/tests/test_repair_logging_integration.py
# Date: 2025-01-14
# Version: 1.0.0
# Description: Integration tests for repair_logging module workflow and cross-doctype functionality
# Dependencies: frappe, pytest

import contextlib

import frappe
from frappe.tests.utils import FrappeTestCase


class TestRepairLoggingIntegration(FrappeTestCase):
    """Test integration workflows for repair_logging module."""

    def setUp(self):
        """Set up test data for integration testing."""
        frappe.set_user("Administrator")

        # Create test customer
        if not frappe.db.exists("Customer", "Test Integration Customer"):
            customer = frappe.get_doc(
                {
                    "doctype": "Customer",
                    "customer_name": "Test Integration Customer",
                    "customer_type": "Individual",
                }
            )
            customer.insert()

        # Create test item
        if not frappe.db.exists("Item", "TEST-CLARINET-001"):
            item = frappe.get_doc(
                {
                    "doctype": "Item",
                    "item_code": "TEST-CLARINET-001",
                    "item_name": "Test Clarinet",
                    "item_group": "Instruments",
                }
            )
            item.insert()

    def test_repair_workflow_integration(self):
        """Test complete repair workflow with logging integration."""
        # Create repair task log
        task_log = frappe.get_doc(
            {
                "doctype": "Repair Task Log",
                "task_name": "Integration Test Repair",
                "task_description": "Test repair task for integration",
                "technician": "Administrator",
                "status": "In Progress",
                "priority": "Medium",
            }
        )
        task_log.insert()

        # Create related material use log
        material_log = frappe.get_doc(
            {
                "doctype": "Material Use Log",
                "material_name": "Test Pad",
                "quantity_used": 2,
                "technician": "Administrator",
                "operation_type": "Repair Task Log",
                "operation_link": task_log.name,
            }
        )
        material_log.insert()

        # Create tool usage log
        tool_log = frappe.get_doc(
            {
                "doctype": "Tool Usage Log",
                "tool_name": "Test Reamer",
                "usage_duration": 30,
                "technician": "Administrator",
                "operation_type": "Repair Task Log",
                "operation_link": task_log.name,
            }
        )
        tool_log.insert()

        # Verify links are maintained
        assert material_log.operation_link == task_log.name
        assert tool_log.operation_link == task_log.name

        # Update task to completed
        task_log.status = "Completed"
        task_log.end_time = frappe.utils.now_datetime()
        task_log.save()

        # Verify cascade behavior
        assert task_log.status == "Completed"

        # Clean up
        material_log.delete()
        tool_log.delete()
        task_log.delete()

    def test_instrument_interaction_tracking(self):
        """Test instrument interaction logging across modules."""
        # Create instrument interaction log
        interaction = frappe.get_doc(
            {
                "doctype": "Instrument Interaction Log",
                "instrument_reference": "TEST-CLARINET-001",
                "interaction_type": "Inspection",
                "technician": "Administrator",
                "notes": "Integration test interaction",
            }
        )
        interaction.insert()

        # Create related visual inspection
        inspection = frappe.get_doc(
            {
                "doctype": "Visual Inspection",
                "instrument_reference": "TEST-CLARINET-001",
                "inspection_type": "Pre-Repair Assessment",
                "inspector": "Administrator",
                "body_condition_rating": 7,
                "key_condition_rating": 8,
            }
        )
        inspection.insert()

        # Verify cross-references
        assert interaction.instrument_reference == inspection.instrument_reference

        # Clean up
        inspection.delete()
        interaction.delete()

    def test_warranty_tracking_integration(self):
        """Test warranty modification tracking integration."""
        # Create warranty modification log
        warranty_log = frappe.get_doc(
            {
                "doctype": "Warranty Modification Log",
                "instrument_reference": "TEST-CLARINET-001",
                "modification_type": "Extension",
                "reason": "Integration test warranty extension",
                "technician": "Administrator",
                "old_warranty_end_date": "2025-12-31",
                "new_warranty_end_date": "2026-12-31",
            }
        )
        warranty_log.insert()

        # Verify calculations
        assert warranty_log.warranty_impact_days is not None
        assert warranty_log.warranty_impact_days > 0

        # Clean up
        warranty_log.delete()

    def test_measurement_data_integrity(self):
        """Test measurement data integrity across different log types."""
        # Create key measurement
        measurement = frappe.get_doc(
            {
                "doctype": "Key Measurement",
                "measurement_name": "Bore Diameter",
                "measurement_value": 14.65,
                "measurement_unit": "mm",
                "instrument_reference": "TEST-CLARINET-001",
                "technician": "Administrator",
            }
        )
        measurement.insert()

        # Create tenon measurement
        tenon = frappe.get_doc(
            {
                "doctype": "Tenon Measurement",
                "instrument_reference": "TEST-CLARINET-001",
                "joint_position": "Upper to Lower",
                "diameter_measurement": 14.60,
                "length_measurement": 25.4,
                "technician": "Administrator",
            }
        )
        tenon.insert()

        # Verify data consistency
        assert measurement.instrument_reference == tenon.instrument_reference
        assert abs(measurement.measurement_value - tenon.diameter_measurement) <= 0.1

        # Clean up
        tenon.delete()
        measurement.delete()

    def tearDown(self):
        """Clean up test data."""
        frappe.set_user("Administrator")

        # Clean up test documents
        for doctype in ["Customer", "Item"]:
            test_docs = frappe.get_all(doctype, filters={"name": ["like", "Test %"]})
            for doc in test_docs:
                with contextlib.suppress(Exception):
                    frappe.delete_doc(doctype, doc.name, force=True)
