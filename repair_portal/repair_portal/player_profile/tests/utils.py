"""Shared test helpers for Player Profile module tests."""

from __future__ import annotations

from datetime import date
from typing import Any

import frappe
from frappe.tests.utils import FrappeTestCase

from repair_portal.player_profile.doctype.player_profile import player_profile


def ensure_email_group() -> None:
    """Guarantee the player newsletter email group exists for tests."""

    if not frappe.db.exists("Email Group", player_profile.PLAYER_NEWSLETTER_GROUP):
        frappe.get_doc(
            {
                "doctype": "Email Group",
                "title": player_profile.PLAYER_NEWSLETTER_GROUP,
            }
        ).insert(ignore_permissions=True)


def create_customer(**overrides: Any) -> frappe.Document:
    data = {
        "doctype": "Customer",
        "customer_name": overrides.pop("customer_name", "Test Customer"),
        "customer_type": overrides.pop("customer_type", "Individual"),
    }
    data.update(overrides)
    doc = frappe.get_doc(data)
    doc.insert(ignore_permissions=True)
    return doc


def create_player_profile(**overrides: Any) -> frappe.Document:
    ensure_email_group()
    customer = overrides.pop("customer", None) or create_customer()
    payload = {
        "doctype": "Player Profile",
        "player_name": overrides.pop("player_name", "Test Player"),
        "primary_email": overrides.pop("primary_email", f"{frappe.generate_hash()[:8]}@example.com"),
        "primary_phone": overrides.pop("primary_phone", "+15555550100"),
        "player_level": overrides.pop("player_level", "Amateur/Hobbyist"),
        "customer": customer.name,
    }
    payload.update(overrides)
    doc = frappe.get_doc(payload)
    doc.insert(ignore_permissions=True)
    return doc


def make_sales_invoice(customer: str, player_profile_name: str, amount: float = 125.0) -> frappe.Document:
    doc = frappe.get_doc(
        {
            "doctype": "Sales Invoice",
            "customer": customer,
            "player_profile": player_profile_name,
            "items": [
                {
                    "item_name": "Service",
                    "rate": amount,
                    "qty": 1,
                }
            ],
        }
    )
    doc.insert(ignore_permissions=True)
    doc.submit()
    return doc


def backdate(dob_years: int) -> date:
    today = date.today()
    return date(today.year - dob_years, today.month, today.day)


class PlayerProfileTestCase(FrappeTestCase):
    def setUp(self) -> None:  # pragma: no cover - invoked by Frappe test runner
        super().setUp()
        ensure_email_group()

    def tearDown(self) -> None:  # pragma: no cover - invoked by Frappe test runner
        frappe.db.delete("Email Group Member", {"email": ["like", "%@example.com%"]})
        super().tearDown()
