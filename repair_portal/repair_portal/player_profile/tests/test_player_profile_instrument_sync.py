"""Instrument synchronization tests for Player Profile."""

from __future__ import annotations

import frappe

from repair_portal.player_profile.tests.utils import PlayerProfileTestCase, create_customer, create_player_profile  # type: ignore


class TestPlayerProfileInstrumentSync(PlayerProfileTestCase):
    def test_instruments_owned_child_table_rebuild(self) -> None:
        customer = create_customer(customer_name="Instrument Customer")
        profile = create_player_profile(customer=customer)

        instrument = frappe.get_doc({
            "doctype": "Instrument",
            "instrument_name": "Clarinet",
            "serial_no": "SYNC-001",
        })
        instrument.insert(ignore_permissions=True)
        self.addCleanup(lambda: frappe.delete_doc("Instrument", instrument.name, force=True))

        instrument_profile = frappe.get_doc({
            "doctype": "Instrument Profile",
            "instrument": instrument.name,
            "customer": customer.name,
        })
        instrument_profile.insert(ignore_permissions=True)
        self.addCleanup(lambda: frappe.delete_doc("Instrument Profile", instrument_profile.name, force=True))

        frappe.db.set_value("Instrument Profile", instrument_profile.name, "owner_player", profile.name)

        profile.reload()
        profile._sync_instruments_owned()
        self.assertEqual(len(profile.instruments_owned), 1)
        row = profile.instruments_owned[0]
        self.assertEqual(row.customer, customer.name)
        self.assertEqual(row.instrument_profile, instrument_profile.name)

        profile.delete(ignore_permissions=True)
        owner_player = frappe.db.get_value("Instrument Profile", instrument_profile.name, "owner_player")
        self.assertFalse(owner_player)
