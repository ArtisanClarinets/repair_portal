"""Tests for loaner validation helpers."""

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
            "first_name": "Loaner",
            "last_name": "Tester",
            "send_welcome_email": 0,
            "roles": [{"role": role} for role in roles],
        }
    )
    user.insert(ignore_permissions=True)
    return email


class TestLoanerFlow(FrappeTestCase):
    """Validate loaner availability checks."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        frappe.set_user("Administrator")
        _load_seed_data()
        cls.user = _ensure_user("loaner.tester@example.com")

    def setUp(self) -> None:
        frappe.set_user(self.user)

    def tearDown(self) -> None:
        frappe.set_user("Administrator")

    def test_loaner_prepare_success(self) -> None:
        response = intake_api.loaner_prepare({"loaner": "LOANER-AVAILABLE-SEED"})
        self.assertEqual(response["loaner"], "LOANER-AVAILABLE-SEED")

    def test_loaner_prepare_rejects_issued(self) -> None:
        with self.assertRaises(frappe.ValidationError):
            intake_api.loaner_prepare({"loaner": "LOANER-ISSUED-SEED"})
