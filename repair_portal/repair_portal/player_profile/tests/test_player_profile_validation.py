"""Validation tests for Player Profile DocType."""

from __future__ import annotations

import frappe
from frappe.exceptions import ValidationError

from repair_portal.player_profile.tests.utils import (  # type: ignore
    PlayerProfileTestCase,
    create_player_profile,
)


class TestPlayerProfileValidation(PlayerProfileTestCase):
    def test_missing_required_fields(self) -> None:
        doc = frappe.get_doc(
            {
                "doctype": "Player Profile",
                "player_name": "",  # missing
                "primary_email": "missing@example.com",
                "primary_phone": "+15555550000",
                "player_level": "Amateur/Hobbyist",
            }
        )
        with self.assertRaises(ValidationError):
            doc.insert(ignore_permissions=True)

    def test_invalid_email_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            create_player_profile(primary_email="invalid-email")

    def test_invalid_phone_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            create_player_profile(primary_phone="invalid#phone")

    def test_duplicate_email_not_allowed(self) -> None:
        email = "duplicate@example.com"
        first = create_player_profile(primary_email=email)
        with self.assertRaises(ValidationError):
            create_player_profile(primary_email=email, player_name="Another")
        first.delete(ignore_permissions=True)
