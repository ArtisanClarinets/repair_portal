"""Tests for Intake Session DocType."""

from __future__ import annotations

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from repair_portal.intake.tasks import cleanup_intake_sessions
from repair_portal.intake.doctype.intake_session.intake_session import _get_session_ttl_days


class TestIntakeSession(FrappeTestCase):
    """Validate Intake Session lifecycle and security."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = "intake.coordinator@example.com"
        if not frappe.db.exists("User", cls.user):
            user = frappe.get_doc(
                {
                    "doctype": "User",
                    "email": cls.user,
                    "first_name": "Intake",
                    "last_name": "Coordinator",
                    "send_welcome_email": 0,
                    "roles": [{"role": "Intake Coordinator"}],
                }
            )
            user.insert(ignore_permissions=True)

        cls.other_user = "intake.viewer@example.com"
        if not frappe.db.exists("User", cls.other_user):
            user = frappe.get_doc(
                {
                    "doctype": "User",
                    "email": cls.other_user,
                    "first_name": "Viewer",
                    "send_welcome_email": 0,
                    "roles": [{"role": "Employee"}],
                }
            )
            user.insert(ignore_permissions=True)

    def tearDown(self) -> None:
        frappe.set_user("Administrator")

    def _new_session(self) -> frappe.model.document.Document:
        frappe.set_user(self.user)
        doc = frappe.get_doc({"doctype": "Intake Session"})
        doc.insert()
        return doc

    def test_defaults_and_autoname(self) -> None:
        doc = self._new_session()
        self.assertTrue(doc.session_id.startswith("ISN-"))
        self.assertEqual(doc.status, "Draft")
        self.assertEqual(doc.created_by, self.user)
        self.assertIsNotNone(doc.expires_on)

    def test_append_event_records_telemetry(self) -> None:
        doc = self._new_session()
        doc.append_event("step_started", {"step": "customer"})
        doc.reload()
        events = doc.intake_json.get("events") if doc.intake_json else []
        self.assertTrue(events)
        self.assertEqual(events[0]["type"], "step_started")
        self.assertEqual(events[0]["payload"]["step"], "customer")

    def test_strong_ownership_enforced(self) -> None:
        doc = self._new_session()
        frappe.set_user(self.other_user)
        doc = frappe.get_doc("Intake Session", doc.name)
        doc.status = "Draft"
        with self.assertRaises(frappe.PermissionError):
            doc.save()

    def test_cleanup_removes_expired_sessions(self) -> None:
        doc = self._new_session()
        frappe.db.set_value("Intake Session", doc.name, "expires_on", add_days(today(), -2))
        frappe.db.set_value("Intake Session", doc.name, "status", "Draft")
        deleted = cleanup_intake_sessions()
        self.assertGreaterEqual(deleted, 1)
        self.assertFalse(frappe.db.exists("Intake Session", doc.name))

    def test_validate_restores_minimum_expiry(self) -> None:
        doc = self._new_session()
        frappe.db.set_value("Intake Session", doc.name, "expires_on", add_days(today(), -5))
        doc.reload()
        doc.save()
        doc.reload()
        expected = add_days(today(), _get_session_ttl_days())
        self.assertEqual(doc.expires_on, expected)
