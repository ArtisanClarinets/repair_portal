"""Integration tests for create_full_intake API."""

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
        doctype = entry.get("doctype")
        name = entry.get("name")
        if not doctype or not name:
            continue
        if frappe.db.exists(doctype, name):
            continue
        doc = frappe.get_doc(entry)
        doc.insert(ignore_permissions=True, ignore_if_duplicate=True)


def _ensure_user(email: str, roles: list[str]) -> str:
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
            "last_name": "QA",
            "send_welcome_email": 0,
            "roles": [{"role": role} for role in roles],
        }
    )
    user.insert(ignore_permissions=True)
    return email


class TestCreateFullIntake(FrappeTestCase):
    """Validate intake creation, idempotency, and permissions."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        frappe.set_user("Administrator")
        _load_seed_data()
        cls.user = _ensure_user(
            "intake.qa@example.com",
            ["System Manager", "Repair Manager", "Intake Coordinator"],
        )
        cls.limited_user = _ensure_user(
            "intake.viewer@example.com",
            ["Employee"],
        )

    def tearDown(self) -> None:
        frappe.set_user("Administrator")

    def _base_payload(self) -> dict[str, object]:
        return {
            "customer": {
                "customer_name": "Seed Customer One",
                "email": "seed.one@example.com",
                "phone": "+1-555-0100",
                "customer_group": "All Customer Groups",
                "territory": "All Territories",
            },
            "instrument": {
                "serial_no": "CI-TEST-0001",
                "brand": "Brand Test Alpha",
                "model": "Model X",
                "clarinet_type": "B♭ Clarinet",
                "instrument_category": "IC-CLARINET-SEED",
            },
            "player": {
                "player_name": "Seed Player",
                "primary_email": "player.one@example.com",
                "player_level": "Student (Advanced)",
            },
            "service": {
                "issue": "Sticky keys",
                "notes": "Requires full cleaning",
                "service_type": "Repair",
                "accessories": [],
            },
            "intake": {
                "intake_type": "Repair",
                "instrument_category": "IC-CLARINET-SEED",
                "manufacturer": "Brand Test Alpha",
                "model": "Model X",
                "clarinet_type": "B♭ Clarinet",
            },
            "loaner": {
                "loaner": "LOANER-AVAILABLE-SEED",
            },
        }

    def test_create_full_intake_happy_path(self) -> None:
        frappe.set_user(self.user)
        payload = self._base_payload()
        result = intake_api.create_full_intake(payload)
        self.assertIn("intake", result)
        self.assertIn("instrument", result)
        intake = frappe.get_doc("Clarinet Intake", result["intake"])
        self.assertEqual(intake.docstatus, 1)
        self.assertIsNotNone(intake.promised_completion_date)
        self.assertEqual(intake.instrument, result["instrument"])
        self.assertEqual(
            intake.player_profile,
            frappe.db.get_value("Player Profile", {"primary_email": "player.one@example.com"}, "name"),
        )
        inspection_name = frappe.db.get_value(
            "Instrument Inspection", {"intake_record_id": intake.name}, "name"
        )
        self.assertIsNotNone(inspection_name)
        self.assertEqual(result.get("loaner"), "LOANER-AVAILABLE-SEED")

    def test_create_full_intake_idempotency(self) -> None:
        frappe.set_user(self.user)
        payload = self._base_payload()
        first = intake_api.create_full_intake(payload)
        second = intake_api.create_full_intake(payload)
        self.assertEqual(first["intake"], second["intake"])

    def test_create_full_intake_permission_denied(self) -> None:
        frappe.set_user(self.limited_user)
        with self.assertRaises(frappe.PermissionError):
            intake_api.create_full_intake(self._base_payload())

    def test_create_full_intake_invalid_serial(self) -> None:
        frappe.set_user(self.user)
        payload = self._base_payload()
        payload["instrument"]["serial_no"] = ""
        with self.assertRaises(frappe.ValidationError):
            intake_api.create_full_intake(payload)
