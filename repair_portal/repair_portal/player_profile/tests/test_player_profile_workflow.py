"""Workflow behavior tests for Player Profile."""

from __future__ import annotations

import frappe
from frappe.exceptions import PermissionError, ValidationError
from frappe.model.workflow import apply_workflow

from repair_portal.player_profile.tests.utils import PlayerProfileTestCase, create_player_profile  # type: ignore


class TestPlayerProfileWorkflow(PlayerProfileTestCase):
    def setUp(self) -> None:
        super().setUp()
        frappe.set_user("Administrator")

    def tearDown(self) -> None:
        frappe.set_user("Administrator")
        super().tearDown()

    def test_workflow_transitions(self) -> None:
        profile = create_player_profile()
        self.assertEqual(profile.profile_status, "Draft")

        apply_workflow(profile, "Activate")
        profile.reload()
        self.assertEqual(profile.profile_status, "Active")

        apply_workflow(profile, "Archive")
        profile.reload()
        self.assertEqual(profile.profile_status, "Archived")

        with self.assertRaises(ValidationError):
            profile.player_name = "Updated"
            profile.save(ignore_permissions=True)

        apply_workflow(profile, "Restore")
        profile.reload()
        self.assertEqual(profile.profile_status, "Draft")

    def test_customer_role_cannot_transition(self) -> None:
        profile = create_player_profile()
        customer_user = frappe.get_doc(
            {
                "doctype": "User",
                "email": "workflow-customer@example.com",
                "first_name": "Workflow",
                "last_name": "Customer",
                "send_welcome_email": 0,
            }
        )
        customer_user.append("roles", {"role": "Customer"})
        customer_user.insert(ignore_permissions=True)
        self.addCleanup(lambda: frappe.delete_doc("User", customer_user.name, force=True))

        frappe.set_user(customer_user.name)
        with self.assertRaises(PermissionError):
            apply_workflow(profile, "Activate")
