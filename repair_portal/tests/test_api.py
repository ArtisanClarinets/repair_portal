import unittest

import frappe
from frappe.exceptions import PermissionError
from frappe.utils import random_string

CLIENT_FIELD = "customer_id"  # Keep in sync with customer.json autoname


class TestCustomerAPI(unittest.TestCase):
    """API-level tests for Customer doctype.

    Each test spins up an Administrator context to create fixtures, then
    switches to a specific role to assert permission behavior. We always set
    ``customer_id`` so the autoname pattern (field:customer_id) is satisfied at
    insert time.
    """

    def setUp(self):
        frappe.set_user("Administrator")

        # -- Create disposable Customer -------------------------------------------------
        self.customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": f"Test Customer {random_string(5)}",
            }
        ).insert(ignore_permissions=True)

        # -- Create Customer -------------------------------------------------------
        self.customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer": self.customer.name,
                CLIENT_FIELD: self.customer.name,  # critical for autoname
            }
        ).insert(ignore_permissions=True)

        frappe.db.commit()

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc("Customer", self.customer.name, force=True)
        frappe.delete_doc("Customer", self.customer.name, force=True)
        frappe.db.commit()

    # ------------------------------------------------------------------
    # READ TESTS
    # ------------------------------------------------------------------
    def test_get_customer_authorized(self):
        frappe.set_user("Client Manager")  # has read rights
        doc = frappe.get_doc("Customer", self.customer.name)
        self.assertEqual(doc.name, self.customer.name)

    def test_get_customer_unauthorized(self):
        frappe.set_user("Guest")
        with self.assertRaises(PermissionError):
            frappe.get_doc("Customer", self.customer.name).check_permissions()

    # ------------------------------------------------------------------
    # WRITE TESTS
    # ------------------------------------------------------------------
    def test_update_customer_authorized(self):
        frappe.set_user("Front Desk")  # write rights
        doc = frappe.get_doc("Customer", self.customer.name)
        doc.notes = "Updated by Front Desk"
        doc.save()
        self.assertEqual(
            frappe.db.get_value("Customer", self.customer.name, "notes"),
            "Updated by Front Desk",
        )

    def test_update_customer_unauthorized(self):
        frappe.set_user("Guest")
        doc = frappe.get_doc("Customer", self.customer.name)
        doc.notes = "Attempted hack"
        with self.assertRaises(PermissionError):
            doc.save()
