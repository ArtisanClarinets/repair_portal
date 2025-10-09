"""Unit tests for customer and player profile upsert helpers."""

from __future__ import annotations

import json
from pathlib import Path

import frappe
from frappe.tests.utils import FrappeTestCase

from repair_portal.intake import api as intake_api

SEED_PATH = Path("repair_portal/repair_portal/fixtures/test_seed.json")


def _load_seed_data() -> None:
    if not SEED_PATH.exists():
        return
    seeds = json.loads(SEED_PATH.read_text())
    for entry in seeds:
        if not entry.get("doctype") or not entry.get("name"):
            continue
        if frappe.db.exists(entry["doctype"], entry["name"]):
            continue
        frappe.get_doc(entry).insert(ignore_permissions=True, ignore_if_duplicate=True)


def _ensure_user(email: str) -> str:
    roles = ["System Manager", "Repair Manager", "Intake Coordinator"]
    if frappe.db.exists("User", email):
        user = frappe.get_doc("User", email)
        existing_roles = {r.role for r in user.roles}
        for role in roles:
            if role not in existing_roles:
                user.append("roles", {"role": role})
        user.save(ignore_permissions=True)
        return email
    user = frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": "Intake",
            "last_name": "Tester",
            "send_welcome_email": 0,
            "roles": [{"role": role} for role in roles],
        }
    )
    user.insert(ignore_permissions=True)
    return email


class TestUpsertHelpers(FrappeTestCase):
    """Ensure upsert helpers remain idempotent."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        frappe.set_user("Administrator")
        _load_seed_data()
        cls.user = _ensure_user("intake.helpers@example.com")

    def setUp(self) -> None:
        frappe.set_user(self.user)

    def tearDown(self) -> None:
        frappe.set_user("Administrator")

    def test_upsert_customer_idempotent(self) -> None:
        payload = {
            "customer_name": "Automation Customer",
            "email": "automation.customer@example.com",
            "phone": "+1-555-0200",
            "address_line1": "123 Repair Ave",
            "city": "Baton Rouge",
            "state": "LA",
            "country": "United States",
            "pincode": "70801",
            "customer_group": "All Customer Groups",
            "territory": "All Territories",
        }
        first = intake_api.upsert_customer(payload)
        second = intake_api.upsert_customer(payload)
        self.assertEqual(first["customer"], second["customer"])
        contact_count = frappe.db.count("Contact", {"email_id": payload["email"]})
        self.assertEqual(contact_count, 1)
        address_links = frappe.db.get_all(
            "Dynamic Link",
            filters={
                "parenttype": "Address",
                "link_doctype": "Customer",
                "link_name": first["customer"],
            },
        )
        self.assertTrue(address_links)

    def test_upsert_player_profile_idempotent(self) -> None:
        payload = {
            "player_name": "Automation Player",
            "primary_email": "automation.player@example.com",
            "primary_phone": "+1-555-0300",
            "player_level": "Amateur/Hobbyist",
        }
        first = intake_api.upsert_player_profile(payload)
        second = intake_api.upsert_player_profile(payload)
        self.assertEqual(first["player_profile"], second["player_profile"])
