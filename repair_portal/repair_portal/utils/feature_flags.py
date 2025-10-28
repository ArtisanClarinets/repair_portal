"""Feature flag utilities for Repair Portal."""
from __future__ import annotations

import frappe


DEFAULT_FLAGS = {
    "enable_mail_in": True,
    "enable_rentals": True,
    "enable_service_plans": True,
    "enable_trials": False,
}


def is_enabled(flag: str) -> bool:
    settings = frappe.get_single("Repair Portal Settings") if frappe.db.exists("DocType", "Repair Portal Settings") else None
    if settings and getattr(settings, flag, None) is not None:
        return bool(getattr(settings, flag))
    return DEFAULT_FLAGS.get(flag, False)

