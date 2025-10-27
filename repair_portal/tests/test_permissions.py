"""Portal permission enforcement tests."""

from __future__ import annotations

from typing import Tuple

import frappe
from frappe.tests.utils import FrappeTestCase

from repair_portal.customer.security import customers_for_user


class TestPortalPermissions(FrappeTestCase):
    def setUp(self) -> None:
        frappe.set_user("Administrator")
        self.customer_a, self.user_a = self._make_customer_with_user("customer-a@example.com")
        self.customer_b, self.user_b = self._make_customer_with_user("customer-b@example.com")
        self.repair_request = frappe.get_doc(
            {
                "doctype": "Repair Request",
                "customer": self.customer_a.name,
                "issue_description": "Sticky pad",
            }
        ).insert()
        self.repair_request.db_set("owner", self.user_a.name)

    def tearDown(self) -> None:  # noqa: D401
        frappe.set_user("Administrator")

    def _make_customer_with_user(self, email: str) -> Tuple[frappe._dict, frappe._dict]:
        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": email,
                "customer_type": "Individual",
            }
        ).insert()
        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "send_welcome_email": 0,
                "first_name": email.split("@")[0],
                "roles": [{"role": "Customer"}],
            }
        ).insert()
        contact = frappe.get_doc(
            {
                "doctype": "Contact",
                "first_name": email.split("@")[0],
                "last_name": "Portal",
                "user": user.name,
                "email_id": email,
            }
        ).insert()
        contact.append("links", {"link_doctype": "Customer", "link_name": customer.name})
        contact.save()
        return customer, user

    def test_customer_only_sees_own_repair_requests(self) -> None:
        frappe.set_user(self.user_b.name)
        records = frappe.get_all(
            "Repair Request",
            filters={"name": self.repair_request.name},
            ignore_permissions=False,
        )
        self.assertEqual(records, [])

        frappe.set_user(self.user_a.name)
        records = frappe.get_all(
            "Repair Request",
            filters={"name": self.repair_request.name},
            ignore_permissions=False,
        )
        self.assertEqual(len(records), 1)

    def test_customer_cannot_access_final_qa(self) -> None:
        frappe.set_user(self.user_a.name)
        has_access = frappe.permissions.has_permission(
            "Final QA Checklist", ptype="read", user=self.user_a.name
        )
        self.assertFalse(has_access)

    def test_customer_mapping_matches_security_helper(self) -> None:
        frappe.set_user(self.user_a.name)
        self.assertIn(self.customer_a.name, customers_for_user(self.user_a.name))
        self.assertNotIn(self.customer_a.name, customers_for_user(self.user_b.name))
