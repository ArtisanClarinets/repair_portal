# Last Updated: 2025-07-13
# Version: 1.0
# Purpose: Validate Player Profile creation, update, and linkage to Client
# Dependencies: Client Profile, Player Profile

import frappe
from frappe.tests.utils import FrappeTestCase

class TestPlayerProfile(FrappeTestCase):

    def setUp(self):
        frappe.set_user("Administrator")
        self.client = frappe.get_doc({
            "doctype": "Client Profile",
            "client_name": "PlayerClient",
            "linked_user": "player@example.com"
        }).insert()

    def test_player_creation(self):
        player = frappe.get_doc({
            "doctype": "Player Profile",
            "first_name": "Alice",
            "last_name": "Reed",
            "client_profile": self.client.name
        }).insert()
        self.assertEqual(player.client_profile, self.client.name)

    def test_update_player_last_name(self):
        player = frappe.get_doc({
            "doctype": "Player Profile",
            "first_name": "Bob",
            "last_name": "Temp",
            "client_profile": self.client.name
        }).insert()
        player.last_name = "Updated"
        player.save()
        self.assertEqual(player.last_name, "Updated")

    def tearDown(self):
        frappe.db.rollback()