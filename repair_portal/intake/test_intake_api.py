"""Integration tests for intake API endpoints."""

from __future__ import annotations

import frappe
from frappe.tests.utils import FrappeTestCase

from repair_portal.intake import api as intake_api
from repair_portal.intake.doctype.brand_mapping_rule.brand_mapping_rule import map_brand
from repair_portal.utils.serials import normalize_serial


class TestIntakeApi(FrappeTestCase):
    """Exercise intake wizard helper endpoints."""

    def setUp(self) -> None:
        frappe.set_user("Administrator")

    def test_get_instrument_by_serial_normalization(self) -> None:
        instrument = frappe.get_doc(
            {
                "doctype": "Instrument",
                "model": "API TEST MODEL",
                "brand": "Acme",
                "serial_no": "AP1-234",
            }
        )
        instrument.insert(ignore_permissions=True)
        response = intake_api.get_instrument_by_serial(" ap1-234 ")
        self.assertTrue(response["match"])
        self.assertEqual(response["normalized_serial"], normalize_serial("ap1-234"))
        self.assertEqual(response["instrument"]["manufacturer"], map_brand("Acme"))

    def test_upsert_customer_idempotent(self) -> None:
        payload = {
            "customer_name": "API Customer",
            "email": "api.customer@example.com",
            "phone": "555-1000",
            "address_line1": "123 Api Lane",
            "city": "Portland",
            "state": "OR",
            "country": "United States",
        }
        first = intake_api.upsert_customer(payload)
        second = intake_api.upsert_customer(payload)
        self.assertEqual(first["customer"], second["customer"])

    def test_upsert_player_profile_idempotent(self) -> None:
        payload = {
            "player_name": "Wizard Player",
            "primary_email": "wizard.player@example.com",
            "player_level": "Professional (Orchestral)",
            "customer": intake_api.upsert_customer(
                {
                    "customer_name": "Wizard Customer",
                    "email": "wizard.customer@example.com",
                    "phone": "555-1001",
                }
            )["customer"],
        }
        result = intake_api.upsert_player_profile(payload)
        payload["preferred_name"] = "Wizard"
        updated = intake_api.upsert_player_profile(payload)
        self.assertEqual(result["player_profile"], updated["player_profile"])

    def test_list_available_loaners(self) -> None:
        instrument = frappe.get_doc(
            {
                "doctype": "Instrument",
                "model": "AVAILABLE LOANER",
                "brand": "Acme",
                "serial_no": "AVL-001",
            }
        )
        instrument.insert(ignore_permissions=True)
        loaner = frappe.get_doc(
            {
                "doctype": "Loaner Instrument",
                "instrument": instrument.name,
                "issue_date": frappe.utils.nowdate(),
                "status": "Returned",
                "returned": 1,
            }
        )
        loaner.insert(ignore_permissions=True)
        rows = intake_api.list_available_loaners({})
        self.assertTrue(any(r["loaner"] == loaner.name for r in rows))

    def test_create_intake_success_and_session_transition(self) -> None:
        session = intake_api.save_intake_session()
        payload = {
            "intake": {
                "intake_type": "New Inventory",
                "manufacturer": "Wizard Co",
                "model": "Wizard 1",
                "serial_no": "WIZ-1001",
                "item_code": "WIZ-1001",
                "item_name": "Wizard Clarinet",
                "acquisition_cost": 1200,
                "store_asking_price": 1800,
            }
        }
        response = intake_api.create_intake(payload, session_id=session["session_id"])
        self.assertIn("intake_name", response)
        self.assertTrue(frappe.db.exists("Clarinet Intake", response["intake_name"]))
        session_doc = frappe.get_doc("Intake Session", session["session_id"])
        self.assertEqual(session_doc.status, "Submitted")
        self.assertFalse(session_doc.error_trace)

    def test_create_intake_rollback_on_failure(self) -> None:
        session = intake_api.save_intake_session()
        with self.assertRaises(frappe.ValidationError):
            intake_api.create_intake({"intake": {"intake_type": "New Inventory"}}, session_id=session["session_id"])
        session_doc = frappe.get_doc("Intake Session", session["session_id"])
        self.assertEqual(session_doc.status, "Abandoned")
        self.assertTrue(session_doc.error_trace)
