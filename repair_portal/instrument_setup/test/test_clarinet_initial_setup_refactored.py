# Last Updated: 2025-07-13
# Version: 1.1
# Purpose: Test Clarinet Initial Setup validation, automation, and PDF enqueue
# Dependencies: Clarinet Initial Setup, Instrument Profile, Item Group

import frappe
from frappe.tests.utils import FrappeTestCase

class TestClarinetInitialSetup(FrappeTestCase):

    def setUp(self):
        frappe.set_user("Administrator")

        # Ensure "All Item Groups" exists
        if not frappe.db.exists("Item Group", "All Item Groups"):
            frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": "All Item Groups",
                "is_group": 1,
                "parent_item_group": None
            }).insert()

        self.client = frappe.get_doc({
            "doctype": "Client Profile",
            "client_name": "SetupTest",
            "linked_user": "setup@example.com"
        }).insert()

        self.player = frappe.get_doc({
            "doctype": "Player Profile",
            "first_name": "Setup",
            "last_name": "Tester",
            "client_profile": self.client.name
        }).insert()

        self.instrument = frappe.get_doc({
            "doctype": "Instrument Profile",
            "instrument_type": "Clarinet",
            "serial_no": "SETUP-2025",
            "player_profile": self.player.name
        }).insert()

    def test_setup_submission_and_pdf(self):
        setup = frappe.get_doc({
            "doctype": "Clarinet Initial Setup",
            "instrument": self.instrument.name,
            "checklist_complete": 1,
            "operations_complete": 1
        })
        setup.insert()
        setup.submit()
        setup.reload()
        self.assertEqual(setup.docstatus, 1)
        self.assertTrue(setup.setup_certificate_status in ["Queued", "Completed"])

    def test_validation_blocks_incomplete_checklist(self):
        setup = frappe.get_doc({
            "doctype": "Clarinet Initial Setup",
            "instrument": self.instrument.name,
            "checklist_complete": 0,
            "operations_complete": 1
        })
        with self.assertRaises(frappe.ValidationError):
            setup.insert()

    def tearDown(self):
        frappe.db.rollback()