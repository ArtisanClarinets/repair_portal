"""Payment request portal integration tests."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

from repair_portal.repair_portal.doctype.customer_approval import payment_hooks
from repair_portal.www import customer_approval


class TestPortalPaymentRequest(FrappeTestCase):
    def setUp(self) -> None:
        frappe.set_user("Administrator")
        self.customer, self.user = self._make_customer_with_user("payment@example.com")
        self.company = frappe.db.get_default("company") or frappe.db.get_value("Company", {}, "name")
        self.item = self._ensure_item()
        self.quotation = frappe.get_doc(
            {
                "doctype": "Quotation",
                "quotation_to": "Customer",
                "party_name": self.customer.name,
                "customer": self.customer.name,
                "transaction_date": today(),
                "company": self.company,
                "items": [
                    {
                        "item_code": self.item.name,
                        "item_name": self.item.item_name,
                        "qty": 1,
                        "rate": 180,
                    }
                ],
            }
        ).insert()
        self.payment_request = frappe.get_doc(
            {
                "doctype": "Payment Request",
                "payment_request_type": "Inward",
                "party_type": "Customer",
                "party": self.customer.name,
                "customer": self.customer.name,
                "transaction_date": today(),
                "reference_doctype": "Quotation",
                "reference_name": self.quotation.name,
                "grand_total": 180,
                "currency": "USD",
                "mode_of_payment": "Cash",
                "status": "Initiated",
                "contact_email": "payment@example.com",
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
                "email_id": email,
            }
        ).insert()
        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": "Payment",
                "send_welcome_email": 0,
                "roles": [{"role": "Customer"}],
            }
        ).insert()
        contact = frappe.get_doc(
            {
                "doctype": "Contact",
                "first_name": "Payment",
                "user": user.name,
                "email_id": email,
            }
        ).insert()
        contact.append("links", {"link_doctype": "Customer", "link_name": customer.name})
        contact.save()
        return customer, user

    def _ensure_item(self):
        existing = frappe.db.get_value("Item", {"item_code": "PORTAL-ITEM"}, "name")
        if existing:
            return frappe.get_doc("Item", existing)
        return frappe.get_doc(
            {
                "doctype": "Item",
                "item_code": "PORTAL-ITEM",
                "item_name": "Portal Service",
                "item_group": frappe.db.get_default("item_group") or "Products",
                "stock_uom": "Nos",
                "is_sales_item": 1,
            }
        ).insert()

    def test_payment_requests_in_portal_context(self) -> None:
        frappe.set_user(self.user.name)
        frappe.local.form_dict = frappe._dict(
            {"reference_doctype": "Quotation", "reference_name": self.quotation.name}
        )
        original_get_doc = frappe.get_doc

        def wrapped_get_doc(*args, **kwargs):
            doc = original_get_doc(*args, **kwargs)
            if isinstance(args[0], str) and args[0] == "Payment Request":
                doc.get_payment_url = lambda: "https://example.com/pay"
            return doc

        with patch("frappe.get_doc", side_effect=wrapped_get_doc):
            context = customer_approval.get_context(SimpleNamespace())
        self.assertTrue(context.payment_requests)
        self.assertEqual(context.payment_requests[0]["payment_url"], "https://example.com/pay")

    def test_payment_request_email_hook(self) -> None:
        self.payment_request.status = "Completed"
        with patch("frappe.sendmail") as sendmail:
            payment_hooks.handle_payment_request_update(self.payment_request, "on_update")
        sendmail.assert_called_once()

        # Second call should not send duplicate email
        with patch("frappe.sendmail") as sendmail:
            payment_hooks.handle_payment_request_update(self.payment_request, "on_update")
        sendmail.assert_not_called()
