"""Regression tests for the Service Plan controller."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import frappe
import pytest
from frappe.tests.utils import FrappeTestCase


class TestServicePlan(FrappeTestCase):
    """Ensure lifecycle automation remains reliable."""

    def test_on_submit_appends_instrument_interaction_log(self) -> None:
        plan = frappe.get_doc(
            {
                "doctype": "Service Plan",
                "name": "PLAN-TEST-001",
                "instrument": "INST-TEST-001",
                "plan_date": frappe.utils.nowdate(),
                "plan_summary": "Seasonal overhaul",
            }
        )

        mocked_profile = MagicMock()

        with patch("frappe.db.exists", return_value=True), patch(
            "frappe.get_doc", return_value=mocked_profile
        ) as get_doc:
            plan.on_submit()

        get_doc.assert_called_once_with("Instrument Profile", "INST-TEST-001")
        mocked_profile.append.assert_called_once_with(
            "interaction_logs",
            {
                "interaction_type": "Service Plan",
                "reference_doctype": "Service Plan",
                "reference_name": "PLAN-TEST-001",
                "date": plan.plan_date,
                "notes": "Seasonal overhaul",
            },
        )
        mocked_profile.save.assert_called_once_with(ignore_permissions=True)

    def test_on_submit_raises_when_instrument_profile_missing(self) -> None:
        plan = frappe.get_doc(
            {
                "doctype": "Service Plan",
                "name": "PLAN-TEST-002",
                "instrument": "INST-UNKNOWN",
                "plan_date": frappe.utils.nowdate(),
                "notes": "Bench check",
            }
        )

        def fake_exists(doctype: str, name: str) -> bool:
            assert doctype == "Instrument Profile"
            assert name == "INST-UNKNOWN"
            return False

        with patch("frappe.db.exists", side_effect=fake_exists), pytest.raises(frappe.ValidationError):
            plan.on_submit()

