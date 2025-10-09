"""Scheduled tasks for intake module."""

from __future__ import annotations

import frappe
from frappe.utils import getdate, today

LOGGER = frappe.logger("intake")


def cleanup_intake_sessions() -> int:
    """Delete expired intake sessions in Draft or Abandoned status."""

    cutoff = getdate(today())
    sessions = frappe.get_all(
        "Intake Session",
        filters={
            "status": ["in", ["Draft", "Abandoned"]],
            "expires_on": ["<", cutoff],
        },
        pluck="name",
    )

    if not sessions:
        return 0

    deleted = 0
    for name in sessions:
        try:
            frappe.delete_doc("Intake Session", name, ignore_permissions=True, force=True)
            deleted += 1
        except Exception:
            LOGGER.error("Failed to cleanup intake session %s", name, exc_info=True)
    if deleted:
        frappe.db.commit()
    return deleted
