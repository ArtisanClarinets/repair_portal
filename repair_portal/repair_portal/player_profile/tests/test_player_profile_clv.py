"""Customer lifetime value tests for Player Profile."""

from __future__ import annotations

import frappe

from repair_portal.player_profile.tests.utils import (  # type: ignore
    PlayerProfileTestCase,
    create_player_profile,
    make_sales_invoice,
)


class TestPlayerProfileCLV(PlayerProfileTestCase):
    def test_sales_invoice_sum_excludes_drafts(self) -> None:
        profile = create_player_profile()
        make_sales_invoice(profile.customer, profile.name, amount=100.0)
        make_sales_invoice(profile.customer, profile.name, amount=250.0)

        draft_invoice = frappe.get_doc(
            {
                "doctype": "Sales Invoice",
                "customer": profile.customer,
                "player_profile": profile.name,
                "items": [
                    {"item_name": "Draft Service", "rate": 999.0, "qty": 1},
                ],
            }
        )
        draft_invoice.insert(ignore_permissions=True)

        profile.reload()
        profile._calculate_clv()
        self.assertEqual(profile.customer_lifetime_value, 350.0)
