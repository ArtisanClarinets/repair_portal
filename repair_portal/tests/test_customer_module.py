"""Tests for customer module DocTypes with database persistence coverage."""

from __future__ import annotations

import unittest

import frappe
from frappe.exceptions import ValidationError
from frappe.model.document import Document
from frappe.tests.utils import FrappeTestCase
from frappe.utils import random_string


class TestCustomerModule(FrappeTestCase):
    """Database-backed tests for Customer module DocTypes."""

    def tearDown(self) -> None:  # pragma: no cover - framework cleanup
        """Rollback database changes after each test."""
        frappe.db.rollback()
        super().tearDown()

    def _create_customer_type(self, **overrides) -> Document:
        """Helper to insert a Customer Type with sensible defaults."""
        type_name = overrides.get("type_name") or f"QA Type {random_string(8)}"
        doc = frappe.get_doc(
            {
                "doctype": "Customer Type",
                "type_name": type_name,
                "is_default": overrides.get("is_default", 0),
                "portal_visible": overrides.get("portal_visible", 1),
                "description": overrides.get("description", "Automated test record"),
            }
        )
        return doc.insert(ignore_permissions=True)

    def test_customer_type_insertion_generates_series_name(self) -> None:
        """Customer Type inserts should allocate a naming series value."""
        customer_type = self._create_customer_type()
        self.assertTrue(customer_type.name.startswith("CPT-"))
        fetched = frappe.get_doc("Customer Type", customer_type.name)
        self.assertEqual(fetched.type_name, customer_type.type_name)

    def test_customer_type_enforces_unique_type_name(self) -> None:
        """Duplicate type_name values should raise a validation error."""
        duplicate_name = f"QA Unique {random_string(6)}"
        self._create_customer_type(type_name=duplicate_name)

        with self.assertRaises(ValidationError):
            self._create_customer_type(type_name=duplicate_name)

    def test_customer_type_default_deduplication(self) -> None:
        """Marking a new default should clear the previous default flag."""
        first = self._create_customer_type(is_default=1)
        second = self._create_customer_type(is_default=1)

        # Reload records to pick up SQL-side updates
        first.reload()
        second.reload()

        self.assertEqual(second.is_default, 1)
        self.assertEqual(first.is_default, 0)

    def test_get_default_customer_type_fallback(self) -> None:
        """Utility method should return the active default or first available type."""
        # Ensure at least one type exists
        customer_type = self._create_customer_type(is_default=1)
        self.assertEqual(
            frappe.get_doc("Customer Type", customer_type.name).get_default_customer_type(),
            customer_type.name,
        )

        # Disable default and verify fallback selects another active entry
        customer_type.is_default = 0
        customer_type.save(ignore_permissions=True)
        alternate = self._create_customer_type(is_default=1)
        self.assertEqual(
            frappe.get_doc("Customer Type", alternate.name).get_default_customer_type(),
            alternate.name,
        )


if __name__ == "__main__":
    unittest.main()
