"""
Tests for repair pulse ownership enforcement.
NOTE: This test requires a running Frappe bench environment.
"""
import frappe
from frappe.tests.utils import FrappeTestCase
from repair_portal.www.mail_in_repair import submit_mail_in_request
import json
from unittest.mock import patch

class TestMailInSecurity(FrappeTestCase):
    def setUp(self):
        # Create a customer and instrument
        # Ensure clean state for serial no
        if frappe.db.exists("Instrument", {"serial_no": "SEC-TEST-001"}):
            frappe.delete_doc("Instrument", frappe.db.get_value("Instrument", {"serial_no": "SEC-TEST-001"}, "name"), force=True)

        self.original_customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "Original Owner",
            "customer_type": "Individual",
            "email_id": "original@example.com"
        }).insert(ignore_permissions=True)

        self.instrument = frappe.get_doc({
            "doctype": "Instrument",
            "customer": self.original_customer.name,
            "serial_no": "SEC-TEST-001",
            "make": "TestMake",
            "model": "TestModel",
            "clarinet_type": "Bb Clarinet"
        }).insert(ignore_permissions=True)

    def tearDown(self):
        # Cleanup
        if frappe.db.exists("Instrument", {"serial_no": "SEC-TEST-001"}):
             frappe.delete_doc("Instrument", frappe.db.get_value("Instrument", {"serial_no": "SEC-TEST-001"}, "name"), force=True)
        # Also clean customers if needed, but Frappe might handle it?
        # Since code commits, we should clean up carefully.
        if frappe.db.exists("Customer", {"email_id": "attacker@example.com"}):
             frappe.delete_doc("Customer", frappe.db.get_value("Customer", {"email_id": "attacker@example.com"}, "name"), force=True)

    @patch("frappe.db.commit")
    def test_instrument_takeover_prevention(self, mock_commit):
        # Attacker tries to submit request with same serial number
        payload = {
            "full_name": "Attacker",
            "email": "attacker@example.com",
            "serial_no": "SEC-TEST-001", # Same serial
            "make": "TestMake",
            "model": "TestModel",
            "family": "Bb",
            "finish": "Silver",
            "requested_services": "Steal this instrument",
            "preferred_carrier": "UPS",
            "insurance_value": 1000,
            "address_line1": "123 Evil St",
            "city": "Bad Town",
            "postal_code": "66666",
            "country": "US",
            "consent_storage": 1
        }

        try:
            submit_mail_in_request(json.dumps(payload))
        except Exception as e:
            # If it throws, that's interesting, but we expect success
            print(f"Submission failed: {e}")

        # Reload instrument
        self.instrument.reload()

        # Check ownership - SHOULD REMAIN ORIGINAL
        # Currently this will fail because the code overwrites it
        self.assertEqual(self.instrument.customer, self.original_customer.name, "Instrument ownership was stolen!")
