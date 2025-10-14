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

    def _ensure_brand(self, name: str) -> str:
        if not frappe.db.exists("Brand", {"brand_name": name}):
            frappe.get_doc({"doctype": "Brand", "brand_name": name}).insert(ignore_permissions=True)
        return name

    def _ensure_category(self, title: str) -> str:
        if not frappe.db.exists("Instrument Category", title):
            frappe.get_doc({"doctype": "Instrument Category", "title": title}).insert(ignore_permissions=True)
        return title

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
        brand = self._ensure_brand("Wizard Co")
        category = self._ensure_category("Clarinet")
        customer_response = intake_api.upsert_customer(
            {
                "customer_name": "Inventory Customer",
                "email": "inventory.customer@example.com",
                "phone": "555-2000",
                "address_line1": "100 Inventory Way",
                "city": "Portland",
                "state": "OR",
                "country": "United States",
            }
        )
        customer_name = customer_response["customer"]
        payload = {
            "customer": {
                "name": customer_name,
                "customer_name": "Inventory Customer",
                "email": "inventory.customer@example.com",
                "phone": "555-2000",
            },
            "instrument": {
                "manufacturer": brand,
                "model": "Wizard 1",
                "serial_no": "WIZ-1001",
                "instrument_category": category,
                "clarinet_type": "B\u266d Clarinet",
                "instrument_type": "B\u266d Clarinet",
                "body_material": "Grenadilla",
                "key_plating": "Silver",
                "accessories": [],
            },
            "player": {
                "sameAsCustomer": True,
                "player_name": "Inventory Customer",
                "primary_email": "inventory.customer@example.com",
                "primary_phone": "555-2000",
                "player_level": "Amateur/Hobbyist",
            },
            "intake": {
                "intake_type": "New Inventory",
                "instrument_category": category,
                "manufacturer": brand,
                "model": "Wizard 1",
                "serial_no": "WIZ-1001",
                "clarinet_type": "B\u266d Clarinet",
                "body_material": "Grenadilla",
                "key_plating": "Silver",
                "item_code": "WIZ-1001",
                "item_name": "Wizard Clarinet",
                "acquisition_cost": 1200,
                "store_asking_price": 1800,
                "customer": customer_name,
                "customer_full_name": "Inventory Customer",
                "customer_email": "inventory.customer@example.com",
                "customer_phone": "555-2000",
            },
        }
        response = intake_api.create_intake(payload, session_id=session["session_id"])
        self.assertIn("intake_name", response)
        self.assertTrue(frappe.db.exists("Clarinet Intake", response["intake_name"]))
        session_doc = frappe.get_doc("Intake Session", session["session_id"])
        self.assertEqual(session_doc.status, "Submitted")
        self.assertFalse(session_doc.error_trace)

    def test_create_intake_success_service_flow(self) -> None:
        session = intake_api.save_intake_session()
        brand = self._ensure_brand("Service Brand")
        category = self._ensure_category("Service Clarinet")
        customer_response = intake_api.upsert_customer(
            {
                "customer_name": "Service Customer",
                "email": "service.customer@example.com",
                "phone": "555-3000",
                "address_line1": "500 Service Ave",
                "city": "Seattle",
                "state": "WA",
                "country": "United States",
            }
        )
        customer_name = customer_response["customer"]
        player_profile = intake_api.upsert_player_profile(
            {
                "player_name": "Service Player",
                "primary_email": "service.player@example.com",
                "primary_phone": "555-3000",
                "player_level": "Professional (Orchestral)",
                "customer": customer_name,
            }
        )["player_profile"]
        payload = {
            "customer": {
                "name": customer_name,
                "customer_name": "Service Customer",
                "email": "service.customer@example.com",
                "phone": "555-3000",
            },
            "instrument": {
                "manufacturer": brand,
                "model": "Service Model",
                "serial_no": "SRV-42",
                "instrument_category": category,
                "clarinet_type": "A Clarinet",
                "instrument_type": "A Clarinet",
                "body_material": "Grenadilla",
                "key_plating": "Silver",
                "accessories": [],
            },
            "player": {
                "sameAsCustomer": False,
                "player_name": "Service Player",
                "primary_email": "service.player@example.com",
                "primary_phone": "555-3000",
                "player_level": "Professional (Orchestral)",
                "profile": player_profile,
            },
            "intake": {
                "intake_type": "Repair",
                "instrument_category": category,
                "manufacturer": brand,
                "model": "Service Model",
                "serial_no": "SRV-42",
                "clarinet_type": "A Clarinet",
                "body_material": "Grenadilla",
                "key_plating": "Silver",
                "item_code": "SRV-42",
                "item_name": "Service Clarinet",
                "customer": customer_name,
                "customer_full_name": "Service Customer",
                "customer_email": "service.customer@example.com",
                "customer_phone": "555-3000",
                "customers_stated_issue": "Cracked tenon",
                "initial_assessment_notes": "Requires tenon graft",
                "player_profile": player_profile,
            },
        }
        response = intake_api.create_intake(payload, session_id=session["session_id"])
        self.assertIn("intake_name", response)
        self.assertTrue(frappe.db.exists("Clarinet Intake", response["intake_name"]))

    def test_create_intake_rollback_on_failure(self) -> None:
        session = intake_api.save_intake_session()
        with self.assertRaises(frappe.ValidationError):
            intake_api.create_intake({"intake": {"intake_type": "New Inventory"}}, session_id=session["session_id"])
        session_doc = frappe.get_doc("Intake Session", session["session_id"])
        self.assertEqual(session_doc.status, "Abandoned")
        self.assertTrue(session_doc.error_trace)
