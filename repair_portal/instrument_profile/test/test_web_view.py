# File: repair_portal/instrument_profile/test/test_web_view.py
# Created: 2025-06-30
# Version: 1.0
# Purpose: Validate public web view for Instrument Profile
# Dev Notes: Ensures published records render via /instrument_profile/<name>

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import set_request
from frappe.website.serve import get_response


class TestInstrumentProfileWebView(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        self.profile = frappe.get_doc(
            {
                "doctype": "Instrument Profile",
                "instrument_category": "Clarinet",
                "serial_number": "WEBVIEW001",
                "route": "webview001",
                "published": 1,
            }
        ).insert()

    def tearDown(self):
        frappe.delete_doc("Instrument Profile", self.profile.name, force=True)

    def test_public_route_json_sanitized(self):
        set_request(
            method="GET",
            path=f"/instrument_profile/{self.profile.name}",
            headers={"Accept": "application/json"},
        )
        response = get_response()
        assert response.status_code == 200
        data = frappe.parse_json(response.get_data(as_text=True))
        assert data.get("name") == self.profile.name
        assert "owner" not in data
