"""Security regression tests for Instrument Serial Number."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase

if TYPE_CHECKING:
    from frappe.model.document import Document


class TestInstrumentSerialNumberSecurity(FrappeTestCase):
    def setUp(self):
        super().setUp()
        frappe.set_user("Administrator")

        if not frappe.db.exists("Brand", "Security ISN Brand"):
            frappe.get_doc({
                "doctype": "Brand",
                "brand": "Security ISN Brand",
            }).insert(ignore_permissions=True)

        self.instrument = frappe.get_doc({
            "doctype": "Instrument",
            "serial_no": f"SEC-ISN-{frappe.generate_hash(length=5)}",
            "brand": "Security ISN Brand",
            "clarinet_type": "Bb Clarinet",
            "current_status": "Active",
        })
        self.instrument.insert(ignore_permissions=True)

        self.isn = frappe.get_doc({
            "doctype": "Instrument Serial Number",
            "serial": f"SECISN-{frappe.generate_hash(length=4)}",
            "instrument": self.instrument.name,
        })
        self.isn.insert(ignore_permissions=True)

        self.addCleanup(lambda: frappe.set_user("Administrator"))

    def tearDown(self):
        if getattr(self, "isn", None):
            frappe.delete_doc("Instrument Serial Number", self.isn.name, force=True, ignore_permissions=True)
        if getattr(self, "instrument", None):
            frappe.delete_doc("Instrument", self.instrument.name, force=True, ignore_permissions=True)
        super().tearDown()

    def _make_user(self, email: str, roles: list[str]) -> 'Document':
        if frappe.db.exists("User", email):
            user = frappe.get_doc("User", email)
        else:
            user = frappe.get_doc(
                {
                    "doctype": "User",
                    "email": email,
                    "first_name": "ISN",
                    "last_name": "Security",
                    "send_welcome_email": 0,
                }
            )
            user.insert(ignore_permissions=True)
        user.add_roles(*roles)
        return user

    def test_attach_requires_permissions_and_logs_denial(self):
        """Customers without write permission must be denied with a security log."""
        customer = self._make_user("isn-security-client@example.com", ["Customer"])
        frappe.set_user(customer.name)

        security_logger = MagicMock()
        audit_logger = MagicMock()

        def _logger(channel: str):
            if channel == "instrument_profile_security":
                return security_logger
            if channel == "instrument_profile_audit":
                return audit_logger
            return MagicMock()

        frappe.cache().delete(f"find_similar_rate_limit:{customer.name}")

        with patch(
            "repair_portal.instrument_profile.doctype.instrument_serial_number.instrument_serial_number.frappe.logger",
            new=_logger,
        ):
            isn_doc = frappe.get_doc("Instrument Serial Number", self.isn.name)
            with self.assertRaises(frappe.PermissionError):
                isn_doc.attach_to_instrument(self.instrument.name)

        self.assertTrue(security_logger.info.called)
        payload = security_logger.info.call_args[0][0]
        self.assertEqual(payload["status"], "denied")
        self.assertEqual(payload["extras"].get("reason"), "no_isn_write_permission")
        self.assertFalse(audit_logger.info.called)

    def test_attach_success_emits_audit_log(self):
        """Administrators attaching an instrument should generate an audit trail."""
        frappe.set_user("Administrator")

        security_logger = MagicMock()
        audit_logger = MagicMock()

        def _logger(channel: str):
            if channel == "instrument_profile_security":
                return security_logger
            if channel == "instrument_profile_audit":
                return audit_logger
            return MagicMock()

        isn_doc = frappe.get_doc("Instrument Serial Number", self.isn.name)

        with patch(
            "repair_portal.instrument_profile.doctype.instrument_serial_number.instrument_serial_number.frappe.logger",
            new=_logger,
        ):
            result = isn_doc.attach_to_instrument(self.instrument.name)

        self.assertEqual(result["instrument"], self.instrument.name)
        self.assertTrue(audit_logger.info.called)
        payload = audit_logger.info.call_args[0][0]
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["extras"].get("target_instrument"), self.instrument.name)

    def test_find_similar_rate_limit_enforced(self):
        """Burst find_similar calls should raise and emit a rate-limit log entry."""
        frappe.set_user("Administrator")
        security_logger = MagicMock()

        def _logger(channel: str):
            if channel == "instrument_profile_security":
                return security_logger
            return MagicMock()

        cache_key = f"find_similar_rate_limit:{frappe.session.user}"
        frappe.cache().delete(cache_key)

        isn_doc = frappe.get_doc("Instrument Serial Number", self.isn.name)

        with patch(
            "repair_portal.instrument_profile.doctype.instrument_serial_number.instrument_serial_number.frappe.logger",
            new=_logger,
        ):
            for _ in range(11):
                isn_doc.find_similar()

            with self.assertRaises(frappe.ValidationError):
                isn_doc.find_similar()

        self.assertTrue(security_logger.info.called)
        payload = security_logger.info.call_args_list[-1][0][0]
        self.assertEqual(payload["status"], "rate_limited")
        self.assertEqual(payload["extras"].get("limit"), 10)
