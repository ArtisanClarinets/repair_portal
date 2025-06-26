# File: repair_portal/instrument_profile/doctype/instrument_profile/test_web_view.py
# Created: 2025-06-27
# Version: 1.0
# Purpose: Validate sanitized context for published Instrument Profile web view

import unittest
import frappe


class TestInstrumentProfileWebView(unittest.TestCase):
    def test_private_fields_sanitized(self):
        doc = frappe.get_doc(
            {
                "doctype": "Instrument Profile",
                "instrument_category": "Clarinet",
                "serial_number": "PUB123",
                "route": "pub123",
                "wellness_score": 50,
                "client_profile": "Client1",
                "published": 1,
            }
        ).insert(ignore_permissions=True, ignore_links=True)

        context = frappe._dict()
        doc.get_context(context)

        assert "owner" not in context.profile
        assert "client_profile" not in context.profile
        assert "wellness_score" not in context.profile

