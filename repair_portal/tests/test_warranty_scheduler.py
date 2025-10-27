"""Warranty reminder scheduler tests."""

from __future__ import annotations

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate

from repair_portal.customer.tasks import warranty


class TestWarrantyScheduler(FrappeTestCase):
    def setUp(self) -> None:
        frappe.set_user("Administrator")
        self.customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": "Warranty Customer",
                "customer_type": "Individual",
                "email_id": "warranty@example.com",
            }
        ).insert()
        self.profile = frappe.get_doc(
            {
                "doctype": "Instrument Profile",
                "instrument_profile_id": "IP-TEST",
                "customer": self.customer.name,
                "instrument": "Clarinet",
                "status": "Active",
                "warranty_end_date": add_days(getdate(), 10),
            }
        ).insert()

    def tearDown(self) -> None:  # noqa: D401
        frappe.set_user("Administrator")

    def test_warranty_reminder_sends_email(self) -> None:
        with patch("frappe.sendmail") as sendmail:
            notified = warranty.dispatch_warranty_reminders(days_ahead=15)
        self.assertIn(self.profile.name, notified)
        sendmail.assert_called_once()
        comment_exists = frappe.db.exists(
            "Comment",
            {
                "reference_doctype": "Instrument Profile",
                "reference_name": self.profile.name,
                "subject": ["like", "Warranty reminder%"],
            },
        )
        self.assertTrue(comment_exists)

    def test_warranty_reminder_idempotent(self) -> None:
        with patch("frappe.sendmail"):
            warranty.dispatch_warranty_reminders(days_ahead=15)
        with patch("frappe.sendmail") as sendmail:
            warranty.dispatch_warranty_reminders(days_ahead=15)
        sendmail.assert_not_called()
