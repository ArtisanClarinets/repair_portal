"""Tests for service plan automation helpers."""
from __future__ import annotations

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from repair_portal.repair_portal.service_plans import automation


class TestServicePlanAutomation(FrappeTestCase):
    """Validate critical automation behaviors."""

    def test_ensure_portal_token_generates_when_missing(self) -> None:
        enrollment = frappe._dict(
            doctype="Service Plan Enrollment",
            name="ENROLL-001",
            portal_token=None,
        )

        with patch(
            "repair_portal.repair_portal.service_plans.automation.token_utils.generate_secure_token",
            return_value="srv-TESTTOKEN",
        ) as generator, patch("frappe.db.set_value") as set_value:
            automation.ensure_portal_token(enrollment)

        generator.assert_called_once_with(prefix="srv")
        set_value.assert_called_once_with(
            "Service Plan Enrollment",
            "ENROLL-001",
            "portal_token",
            "srv-TESTTOKEN",
        )

    def test_ensure_portal_token_skips_existing_value(self) -> None:
        enrollment = frappe._dict(
            doctype="Service Plan Enrollment",
            name="ENROLL-002",
            portal_token="existing-token",
        )

        with patch(
            "repair_portal.repair_portal.service_plans.automation.token_utils.generate_secure_token"
        ) as generator, patch("frappe.db.set_value") as set_value:
            automation.ensure_portal_token(enrollment)

        generator.assert_not_called()
        set_value.assert_not_called()

