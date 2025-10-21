# Path: repair_portal/repair_logging/tests/test_repair_logging_performance.py
# Date: 2025-01-14
# Version: 1.0.0
# Description: Performance tests for repair_logging module queries and operations
# Dependencies: frappe, pytest, time

import time

import frappe
from frappe.tests.utils import FrappeTestCase


class TestRepairLoggingPerformance(FrappeTestCase):
    """Test performance characteristics of repair_logging module."""

    def setUp(self):
        """Set up test data for performance testing."""
        frappe.set_user("Administrator")

    def test_bulk_insert_performance(self):
        """Test performance of bulk insert operations."""
        start_time = time.time()

        # Create multiple test documents
        docs = []
        for i in range(10):
            doc = frappe.get_doc(
                {
                    "doctype": "Material Use Log",
                    "material_name": f"Test Material {i}",
                    "quantity_used": i + 1,
                    "technician": "Administrator",
                }
            )
            docs.append(doc)

        # Insert all docs
        for doc in docs:
            doc.insert()

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time
        assert duration < 5.0, "Bulk insert took too long"

        # Clean up
        for doc in docs:
            doc.delete()

    def test_query_performance_with_indexes(self):
        """Test that queries perform well with proper indexing."""
        # Create test data
        doc = frappe.get_doc(
            {
                "doctype": "Repair Task Log",
                "task_name": "Performance Test Task",
                "status": "In Progress",
                "technician": "Administrator",
            }
        )
        doc.insert()

        start_time = time.time()

        # Query that should use indexes
        frappe.get_all(
            "Repair Task Log",
            filters={"status": "In Progress"},
            fields=["name", "task_name", "technician"],
            limit=100,
        )

        end_time = time.time()
        query_time = end_time - start_time

        # Should be fast
        assert query_time < 1.0, "Query took too long"

        # Clean up
        doc.delete()

    def test_timeline_loading_performance(self):
        """Test customer timeline loading performance."""
        start_time = time.time()

        # Simulate loading customer interactions
        frappe.get_all(
            "Instrument Interaction Log", fields=["name", "interaction_type", "notes", "creation"], limit=50
        )

        end_time = time.time()
        load_time = end_time - start_time

        # Should load quickly
        assert load_time < 2.0, "Timeline loading took too long"

    def tearDown(self):
        """Clean up test data."""
        frappe.set_user("Administrator")
