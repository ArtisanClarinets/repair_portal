"""Customer approval workflow tests."""

from __future__ import annotations

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

from repair_portal.repair_portal.doctype.customer_approval.customer_approval import (
    CustomerApproval,
    create_customer_approval,
)


class TestCustomerApproval(FrappeTestCase):
    def setUp(self) -> None:
        frappe.set_user("Administrator")
        self.customer, self.user = self._make_customer_with_user("approval@example.com")
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
                        "description": self.item.description or self.item.item_name,
                        "qty": 1,
                        "rate": 250,
                    }
                ],
            }
        ).insert()

    def tearDown(self) -> None:  # noqa: D401
        frappe.set_user("Administrator")

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
                "first_name": "Approval",
                "send_welcome_email": 0,
                "roles": [{"role": "Customer"}],
            }
        ).insert()
        contact = frappe.get_doc(
            {
                "doctype": "Contact",
                "first_name": "Approval",
                "last_name": "Portal",
                "user": user.name,
                "email_id": email,
            }
        ).insert()
        contact.append("links", {"link_doctype": "Customer", "link_name": customer.name})
        contact.save()
        return customer, user

    def test_create_customer_approval(self) -> None:
        frappe.set_user(self.user.name)
        with patch("frappe.attach_print") as attach_print, patch("frappe.sendmail") as sendmail:
            attach_print.return_value = {"fname": "customer-approval.pdf"}
            approval = create_customer_approval(
                reference_doctype="Quotation",
                reference_name=self.quotation.name,
                action="Approved",
                signer_full_name="Approval User",
                signer_email="approval@example.com",
                signer_phone="555-1000",
                note="Proceed with work",
                terms_version="v1",
                terms_consent=True,
            )
        self.assertIsInstance(approval, CustomerApproval)
        self.assertEqual(approval.portal_user, self.user.name)
        self.assertEqual(approval.action, "Approved")
        self.assertEqual(approval.approval_pdf, "customer-approval.pdf")
        sendmail.assert_called_once()
        rendered = frappe.render_template(
            "repair_portal/templates/emails/customer_approval_received.html",
            {"doc": approval, "reference_url": "https://example.com"},
        )
        self.assertIn("Approval User", rendered)
        with self.assertRaises(frappe.DuplicateEntryError):
            create_customer_approval(
                reference_doctype="Quotation",
                reference_name=self.quotation.name,
                action="Approved",
                signer_full_name="Approval User",
                signer_email="approval@example.com",
                signer_phone="555-1000",
                note="Duplicate",
                terms_version="v1",
                terms_consent=True,
            )

    def test_customer_approval_is_immutable(self) -> None:
        frappe.set_user(self.user.name)
        with patch("frappe.attach_print") as attach_print, patch("frappe.sendmail"):
            attach_print.return_value = {"fname": "customer-approval.pdf"}
            approval = create_customer_approval(
                reference_doctype="Quotation",
                reference_name=self.quotation.name,
                action="Approved",
                signer_full_name="Approval User",
                signer_email="approval@example.com",
                signer_phone="555-1000",
                note="Proceed",
                terms_version="v1",
                terms_consent=True,
            )
        approval.note = "Changed"
        with self.assertRaises(frappe.ValidationError):
            approval.save()
