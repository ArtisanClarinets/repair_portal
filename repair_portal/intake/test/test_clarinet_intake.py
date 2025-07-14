# Last Updated: 2025-07-13
# Version: 1.0
# Purpose: Validate Clarinet Intake lifecycle, checklist validation, and escalation triggers
# Dependencies: Client Profile, Player Profile, Instrument Profile, Clarinet Intake

import frappe
from frappe.tests.utils import FrappeTestCase

class TestClarinetIntake(FrappeTestCase):

    def setUp(self):
        frappe.set_user("Administrator")
        self.client = frappe.get_doc({
            "doctype": "Client Profile",
            "client_name": "Intake Tester",
            "linked_user": "test@example.com"
        }).insert()

        self.player = frappe.get_doc({
            "doctype": "Player Profile",
            "first_name": "Jane",
            "last_name": "Doe",
            "client_profile": self.client.name
        }).insert()

        self.instrument = frappe.get_doc({
            "doctype": "Instrument Profile",
            "instrument_type": "Clarinet",
            "serial_no": "INTAKE-001",
            "player_profile": self.player.name
        }).insert()

    def test_intake_creation_and_defaults(self):
        intake = frappe.get_doc({
            "doctype": "Clarinet Intake",
            "instrument": self.instrument.name,
            "player": self.player.name,
            "client": self.client.name,
            "intake_type": "Repair",
            "checklist_complete": 1
        }).insert()
        intake.reload()
        self.assertEqual(intake.status, "Pending Inspection")

    def test_checklist_validation_failure(self):
        intake = frappe.get_doc({
            "doctype": "Clarinet Intake",
            "instrument": self.instrument.name,
            "player": self.player.name,
            "client": self.client.name,
            "intake_type": "Repair",
            "checklist_complete": 0
        })
        with self.assertRaises(frappe.ValidationError):
            intake.insert()

    def tearDown(self):
        frappe.db.rollback()