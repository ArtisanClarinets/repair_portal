"""Service history aggregation tests for Player Profile."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

import frappe

from repair_portal.player_profile.doctype.player_profile import player_profile
from repair_portal.player_profile.tests.utils import PlayerProfileTestCase, create_player_profile  # type: ignore


class TestPlayerProfileServiceHistory(PlayerProfileTestCase):
    def test_service_history_sorted(self) -> None:
        profile = create_player_profile()
        with patch("frappe.get_all") as get_all:
            get_all.side_effect = [
                [
                    {
                        "name": "INTAKE-1",
                        "received_date": date(2024, 1, 15),
                        "serial_no": "SER123",
                        "status": "Received",
                    }
                ],
                [
                    {
                        "name": "RO-1",
                        "posting_date": date(2024, 2, 10),
                        "status": "Completed",
                        "serial_no": "SER123",
                    }
                ],
            ]
            history = player_profile.get_service_history(profile.name)

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["reference"], "RO-1")
        self.assertEqual(history[0]["type"], "Repair Order")
        self.assertEqual(history[1]["reference"], "INTAKE-1")
