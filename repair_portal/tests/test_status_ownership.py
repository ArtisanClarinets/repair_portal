"""Tests for repair pulse ownership enforcement."""

from __future__ import annotations

from types import SimpleNamespace

import frappe
from frappe.tests.utils import FrappeTestCase

from repair_portal.www import repair_pulse


class TestStatusOwnership(FrappeTestCase):
    def setUp(self) -> None:
        frappe.set_user("Administrator")
        self.customer_a, self.user_a = self._make_customer_with_user("pulse-a@example.com")
        self.customer_b, self.user_b = self._make_customer_with_user("pulse-b@example.com")
        self.repair_request = frappe.get_doc(
            {
                "doctype": "Repair Request",
                "customer": self.customer_a.name,
                "issue_description": "Cracked tenon",
            }
        ).insert()
        self.repair_request.db_set("owner", self.user_a.name)
        for status in ("Intake", "In Progress"):
            frappe.get_doc(
                {
                    "doctype": "Pulse Update",
                    "repair_request": self.repair_request.name,
                    "status": status,
                    "details": f"Status changed to {status}",
                }
            ).insert()

    def tearDown(self) -> None:  # noqa: D401
        frappe.set_user("Administrator")
        frappe.local.form_dict = frappe._dict()

    def _make_customer_with_user(self, email: str):
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
                "first_name": email.split("@")[0],
                "send_welcome_email": 0,
                "roles": [{"role": "Customer"}],
            }
        ).insert()
        contact = frappe.get_doc(
            {
                "doctype": "Contact",
                "first_name": email.split("@")[0],
                "user": user.name,
                "email_id": email,
            }
        ).insert()
        contact.append("links", {"link_doctype": "Customer", "link_name": customer.name})
        contact.save()
        return customer, user

    def test_owner_can_fetch_updates(self) -> None:
        frappe.set_user(self.user_a.name)
        frappe.local.form_dict = frappe._dict({"name": self.repair_request.name})
        context = SimpleNamespace()
        result = repair_pulse.get_context(context)
        self.assertEqual(len(result.updates), 2)

    def test_other_customer_blocked(self) -> None:
        frappe.set_user(self.user_b.name)
        frappe.local.form_dict = frappe._dict({"name": self.repair_request.name})
        with self.assertRaises(frappe.PermissionError):
            repair_pulse.get_context(SimpleNamespace())
