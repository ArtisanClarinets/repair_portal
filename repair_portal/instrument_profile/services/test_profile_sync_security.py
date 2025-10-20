"""Security regression tests for Instrument Profile sync services."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch, call

import frappe
from frappe.tests.utils import FrappeTestCase

from repair_portal.instrument_profile.services import profile_sync

if TYPE_CHECKING:
    from frappe.model.document import Document


class TestProfileSyncSecurity(FrappeTestCase):
    def setUp(self):
        super().setUp()
        frappe.set_user("Administrator")

        if not frappe.db.exists("Brand", "Security Sync Brand"):
            frappe.get_doc(
                {
                    "doctype": "Brand",
                    "brand": "Security Sync Brand",
                }
            ).insert(ignore_permissions=True)

        self.instrument = frappe.get_doc(
            {
                "doctype": "Instrument",
                "serial_no": f"SEC-SYNC-{frappe.generate_hash(length=5)}",
                "brand": "Security Sync Brand",
                "clarinet_type": "Bb Clarinet",
                "current_status": "Active",
            }
        )
        self.instrument.insert(ignore_permissions=True)

        self.profile = frappe.get_doc(
            {
                "doctype": "Instrument Profile",
                "instrument": self.instrument.name,
                "serial_no": "stale",
                "brand": "Outdated",
            }
        )
        self.profile.insert(ignore_permissions=True)

        self.addCleanup(lambda: frappe.set_user("Administrator"))

    def tearDown(self):
        if getattr(self, "profile", None):
            frappe.delete_doc("Instrument Profile", self.profile.name, force=True, ignore_permissions=True)
        if getattr(self, "instrument", None):
            frappe.delete_doc("Instrument", self.instrument.name, force=True, ignore_permissions=True)
        super().tearDown()

    def _make_user(self, email: str, roles: list[str]) -> "Document":
        if frappe.db.exists("User", email):
            user = frappe.get_doc("User", email)
        else:
            user = frappe.get_doc(
                {
                    "doctype": "User",
                    "email": email,
                    "first_name": "Profile",
                    "last_name": "Security",
                    "send_welcome_email": 0,
                }
            )
            user.insert(ignore_permissions=True)
        user.add_roles(*roles)
        return user

    def test_sync_now_denied_without_profile_permission(self):
        """Users without write permission must be blocked and logged."""
        user = self._make_user("profile-sync-client@example.com", ["Customer"])
        frappe.set_user(user.name)

        security_logger = MagicMock()

        def _logger(channel: str):
            if channel == "instrument_profile_security":
                return security_logger
            return MagicMock()

        with patch(
            "repair_portal.instrument_profile.services.profile_sync.frappe.logger",
            new=_logger,
        ):
            with self.assertRaises(frappe.PermissionError):
                profile_sync.sync_now(profile=self.profile.name)

        payload = security_logger.info.call_args[0][0]
        self.assertEqual(payload["status"], "denied")
        self.assertEqual(payload["extras"].get("reason"), "no_profile_write_permission")

    def test_sync_now_denied_without_instrument_permission(self):
        """Instrument read checks must be enforced and logged."""
        user = self._make_user("profile-sync-client2@example.com", ["Customer"])
        frappe.set_user(user.name)

        security_logger = MagicMock()

        def _logger(channel: str):
            if channel == "instrument_profile_security":
                return security_logger
            return MagicMock()

        with patch(
            "repair_portal.instrument_profile.services.profile_sync.frappe.logger",
            new=_logger,
        ):
            with self.assertRaises(frappe.PermissionError):
                profile_sync.sync_now(instrument=self.instrument.name)

        payload = security_logger.info.call_args[0][0]
        self.assertEqual(payload["doctype"], "Instrument")
        self.assertEqual(payload["status"], "denied")
        self.assertEqual(payload["extras"].get("reason"), "no_instrument_read_permission")

    def test_sync_now_batches_db_updates_and_logs_job_event(self):
        """Successful sync writes once and emits a job log entry."""
        frappe.set_user("Administrator")

        # Ensure there are differences so an update occurs
        frappe.db.set_value(
            "Instrument",
            self.instrument.name,
            {
                "brand": "Security Sync Brand",
                "clarinet_type": "Bb Clarinet",
                "current_status": "Active",
            },
        )

        security_logger = MagicMock()
        job_logger = MagicMock()

        def _logger(channel: str):
            if channel == "instrument_profile_security":
                return security_logger
            if channel == "instrument_profile_jobs":
                return job_logger
            return MagicMock()

        with (
            patch(
                "repair_portal.instrument_profile.services.profile_sync.frappe.logger",
                new=_logger,
            ),
            patch(
                "repair_portal.instrument_profile.services.profile_sync.frappe.db.set_value",
                wraps=frappe.db.set_value,
            ) as patched_set_value,
        ):
            result = profile_sync.sync_now(profile=self.profile.name)

        self.assertEqual(result["profile"], self.profile.name)
        self.assertTrue(job_logger.info.called)
        job_payload = job_logger.info.call_args_list[-1][0][0]
        self.assertEqual(job_payload["status"], "success")
        self.assertEqual(job_payload["extras"].get("instrument"), self.instrument.name)

        calls = [call for call in patched_set_value.call_args_list if call[0][0] == "Instrument Profile"]
        self.assertEqual(len(calls), 1)
        updated_fields = calls[0][0][2]
        self.assertIsInstance(updated_fields, dict)
        self.assertGreaterEqual(len(updated_fields.keys()), 3)
