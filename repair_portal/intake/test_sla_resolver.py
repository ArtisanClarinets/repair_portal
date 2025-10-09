"""Tests for SLA resolver utilities."""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime

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
            "first_name": "SLA",
            "last_name": "Tester",
            "send_welcome_email": 0,
            "roles": [{"role": role} for role in roles],
        }
    )
    user.insert(ignore_permissions=True)
    return email


class TestSLAResolver(FrappeTestCase):
    """Ensure SLA computation behaves as expected."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        frappe.set_user("Administrator")
        _load_seed_data()
        settings = frappe.get_single("Clarinet Intake Settings")
        settings.sla_target_hours = 48
        settings.sla_label = "Promise by"
        settings.save(ignore_permissions=True)
        cls.user = _ensure_user("sla.tester@example.com")

    def setUp(self) -> None:
        frappe.set_user(self.user)

    def tearDown(self) -> None:
        frappe.set_user("Administrator")

    def _payload(self) -> dict[str, object]:
        return {
            "customer": {
                "customer_name": "Seed Customer Two",
                "email": "seed.two@example.com",
                "phone": "+1-555-0101",
                "customer_group": "All Customer Groups",
                "territory": "All Territories",
            },
            "instrument": {
                "serial_no": "CI-SLA-0001",
                "brand": "Brand Test Alpha",
                "model": "Model SLA",
                "clarinet_type": "B♭ Clarinet",
                "instrument_category": "IC-CLARINET-SEED",
            },
            "intake": {
                "intake_type": "Repair",
                "instrument_category": "IC-CLARINET-SEED",
                "manufacturer": "Brand Test Alpha",
                "model": "Model SLA",
                "clarinet_type": "B♭ Clarinet",
            },
            "service": {"issue": "SLA validation"},
        }

    def test_resolve_sla_returns_expected_offset(self) -> None:
        before = now_datetime()
        result = intake_api.resolve_sla({})
        after = now_datetime()
        target = result["target_dt"]
        self.assertIsNotNone(target)
        delta = target - before
        self.assertTrue(timedelta(hours=48) <= delta <= (after - before) + timedelta(hours=48, minutes=1))
        self.assertEqual(result["label"], "Promise by")

    def test_create_full_intake_sets_promised_completion(self) -> None:
        payload = self._payload()
        result = intake_api.create_full_intake(payload)
        intake = frappe.get_doc("Clarinet Intake", result["intake"])
        self.assertIsNotNone(intake.promised_completion_date)
