"""Operational helpers for the clarinet estimator."""

from __future__ import annotations

import frappe
from frappe import _

from repair_portal.customer.security import customers_for_user
from repair_portal.service_planning.clarinet_estimator import (
    UploadedPhoto,
    process_estimate_submission,
)


def smoke(serial: str = "ESTIMATOR-DEMO-1", instrument_family: str = "B\u266d Clarinet", expedite: int = 0) -> dict:
    """Create or refresh a demo estimator submission for smoke testing."""

    frappe.only_for(("System Manager", "Repair Manager", "Administrator"))
    user = frappe.db.get_value("Has Role", {"role": "Customer"}, "parent")
    if not user:
        raise frappe.DoesNotExistError(_("Create a Customer portal user before running the estimator smoke test."))
    linked = customers_for_user(user)
    if not linked:
        raise frappe.DoesNotExistError(_("The selected portal user is not linked to a Customer."))

    selections = ["upper_stack", "bell_tenon"] if instrument_family == "B\u266d Clarinet" else ["lower_stack"]
    photo = UploadedPhoto(filename="demo-estimate.jpg", content=b"demo")

    frappe.logger().info("Running estimator smoke test for %s (%s)", user, instrument_family)
    previous_user = frappe.session.user
    try:
        frappe.set_user(user)
        result = process_estimate_submission(
            user=user,
            instrument_family=instrument_family,
            serial=serial,
            condition_score=70,
            expedite=bool(int(expedite)),
            selections=selections,
            notes="Smoke test submission",
            photo_uploads=[photo],
        )
    finally:
        frappe.set_user(previous_user)

    return {
        "estimate": result.estimate_name,
        "artifact": result.artifact_name,
        "total": result.total,
        "eta_days": result.eta_days,
    }
