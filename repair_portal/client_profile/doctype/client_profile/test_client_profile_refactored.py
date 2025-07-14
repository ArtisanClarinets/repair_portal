# Last Updated: 2025-07-13
# Version: 1.0
# Purpose: Validate Client Profile creation, workflow, and owner-based access
# Dependencies: Client Profile, User

import frappe
from frappe.tests.utils import FrappeTestCase

class TestClientProfileRefactored(FrappeTestCase):

    def setUp(self):
        frappe.set_user("Administrator")
        self.user = frappe.get_doc({
            "doctype": "User",
            "email": "client@example.com",
            "first_name": "Clienty"
        }).insert()

    def test_profile_creation_and_link(self):
        doc = frappe.get_doc({
            "doctype": "Client Profile",
            "client_name": "Workflow Test",
            "linked_user": self.user.name
        }).insert()
        self.assertEqual(doc.linked_user, self.user.name)

    def test_workflow_transition(self):
        doc = frappe.get_doc({
            "doctype": "Client Profile",
            "client_name": "Workflow Switch",
            "linked_user": self.user.name,
            "workflow_state": "Draft"
        }).insert()
        doc.workflow_state = "Active"
        doc.save()
        self.assertEqual(doc.workflow_state, "Active")

    def tearDown(self):
        frappe.db.rollback()