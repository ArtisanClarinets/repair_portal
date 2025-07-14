# Last Updated: 2025-07-13
# Version: 1.0
# Purpose: Validate Instrument Profile creation, uniqueness, and automation hooks
# Dependencies: Player Profile, Instrument Profile

import frappe
from frappe.tests.utils import FrappeTestCase

class TestInstrumentProfile(FrappeTestCase):

    def setUp(self):
        frappe.set_user("Administrator")
        self.client = frappe.get_doc({
            "doctype": "Client Profile",
            "client_name": "InstTest",
            "linked_user": "inst@example.com"
        }).insert()

        self.player = frappe.get_doc({
            "doctype": "Player Profile",
            "first_name": "Instrument",
            "last_name": "Tester",
            "client_profile": self.client.name
        }).insert()

    def test_serial_uniqueness(self):
        serial = "CLTEST-2025"
        doc1 = frappe.get_doc({
            "doctype": "Instrument Profile",
            "instrument_type": "Clarinet",
            "serial_number": serial,
            "player_profile": self.player.name
        }).insert()

        with self.assertRaises(frappe.DuplicateEntryError):
            frappe.get_doc({
                "doctype": "Instrument Profile",
                "instrument_type": "Clarinet",
                "serial_number": serial,
                "player_profile": self.player.name
            }).insert()

    def test_qr_code_update_hook(self):
        inst = frappe.get_doc({
            "doctype": "Instrument Profile",
            "instrument_type": "Clarinet",
            "serial_number": "QR999",
            "player_profile": self.player.name
        }).insert()
        inst.reload()
        self.assertTrue(inst.qr_code or inst.qr_image)

    def tearDown(self):
        frappe.db.rollback()