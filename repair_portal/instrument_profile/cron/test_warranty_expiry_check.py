"""Unit tests covering warranty notification throttling helpers."""

from __future__ import annotations

import frappe
from frappe.tests.utils import FrappeTestCase

from repair_portal.instrument_profile.cron import warranty_expiry_check as warranty


class TestWarrantyExpiryThrottle(FrappeTestCase):
    def setUp(self):
        super().setUp()
        frappe.set_user("Administrator")

    def test_within_daily_limit_enforces_cap(self):
        recipient = "throttle@example.com"
        category = "customer:expiring"
        key = warranty._recipient_throttle_key(recipient, category)
        frappe.cache().delete(key)

        self.assertTrue(warranty._within_daily_limit(recipient, category, limit=2))
        self.assertTrue(warranty._within_daily_limit(recipient, category, limit=2))
        self.assertFalse(warranty._within_daily_limit(recipient, category, limit=2))

    def test_throttle_is_case_insensitive(self):
        category = "admin:early"
        key = warranty._recipient_throttle_key("Admin@Example.com", category)
        frappe.cache().delete(key)

        self.assertTrue(warranty._within_daily_limit("Admin@Example.com", category, limit=1))
        self.assertFalse(warranty._within_daily_limit("admin@example.com", category, limit=1))
