"""API permission tests for Player Profile portal endpoints."""

from __future__ import annotations

import frappe
from frappe.exceptions import PermissionError

from repair_portal.player_profile.doctype.player_profile import player_profile
from repair_portal.player_profile.tests.utils import PlayerProfileTestCase, create_player_profile  # type: ignore


class TestPlayerProfileAPIPermissions(PlayerProfileTestCase):
    def setUp(self) -> None:
        super().setUp()
        frappe.set_user("Administrator")

    def tearDown(self) -> None:
        frappe.set_user("Administrator")
        super().tearDown()

    def _make_portal_user(self, email: str) -> str:
        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": email.split("@")[0].title(),
                "send_welcome_email": 0,
            }
        )
        user.append("roles", {"role": "Customer"})
        user.insert(ignore_permissions=True)
        self.addCleanup(lambda: frappe.delete_doc("User", user.name, force=True))
        return user.name

    def test_portal_user_can_read_own_profile(self) -> None:
        profile = create_player_profile(primary_email="portal-user@example.com")
        user_id = self._make_portal_user(profile.primary_email)

        frappe.set_user(user_id)
        fetched = player_profile.get()
        self.assertEqual(fetched["name"], profile.name)

    def test_portal_user_cannot_edit_restricted_field(self) -> None:
        profile = create_player_profile(primary_email="portal-guard@example.com")
        user_id = self._make_portal_user(profile.primary_email)

        frappe.set_user(user_id)
        allowed_payload = {
            "doctype": "Player Profile",
            "name": profile.name,
            "preferred_name": "Friend",
        }
        player_profile.save(frappe.as_json(allowed_payload))
        profile.reload()
        self.assertEqual(profile.preferred_name, "Friend")

        disallowed_payload = {
            "doctype": "Player Profile",
            "name": profile.name,
            "profile_status": "Active",
        }
        with self.assertRaises(PermissionError):
            player_profile.save(frappe.as_json(disallowed_payload))

    def test_identity_must_match_session_user(self) -> None:
        profile = create_player_profile(primary_email="locked@example.com")
        self._make_portal_user(profile.primary_email)
        other_user = self._make_portal_user("other@example.com")

        frappe.set_user(other_user)
        with self.assertRaises(PermissionError):
            player_profile.get()

    def test_portal_user_marketing_update_requires_permissions(self) -> None:
        profile = create_player_profile(primary_email="marketing@example.com")
        user_id = self._make_portal_user(profile.primary_email)
        frappe.set_user(user_id)

        with self.assertRaises(PermissionError):
            player_profile.update_marketing_preferences(profile.name, newsletter=1)

        frappe.set_user("Administrator")
        result = player_profile.update_marketing_preferences(profile.name, newsletter=1)
        self.assertEqual(result["newsletter_subscription"], 1)
