"""COPPA compliance tests for Player Profile."""

from __future__ import annotations

import frappe

from repair_portal.player_profile.doctype.player_profile import player_profile
from repair_portal.player_profile.tests.utils import backdate, create_player_profile, PlayerProfileTestCase  # type: ignore


class TestPlayerProfileCOPPA(PlayerProfileTestCase):
    def test_underage_player_marketing_disabled(self) -> None:
        profile = create_player_profile(
            date_of_birth=backdate(10),
            newsletter_subscription=1,
            targeted_marketing_optin=1,
        )
        profile.reload()
        self.assertEqual(profile.newsletter_subscription, 0)
        self.assertEqual(profile.targeted_marketing_optin, 0)

        member = frappe.db.exists(
            "Email Group Member",
            {
                "email": profile.primary_email,
                "email_group": player_profile.PLAYER_NEWSLETTER_GROUP,
            },
        )
        self.assertIsNone(member)
