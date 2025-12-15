# Path: repair_portal/instrument_profile/api.py
# Date: 2025-12-15
# Version: 0.1.0
# Description: Simple API helpers for Instrument Profile UI features (polling, lightweight status checks).
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe.utils import get_datetime, now_datetime
from datetime import timedelta


@frappe.whitelist()
def check_pending_updates(last_update: str = "") -> dict:
    """Return a simple payload indicating whether any Instrument Profile records
    have been modified since `last_update` (ISO format). If `last_update` is
    blank, look for updates in the last 60 seconds.

    Used by the enhanced Instrument Profile ListView to show a refresh hint.
    """
    try:
        if not last_update:
            cutoff = now_datetime() - timedelta(seconds=60)
        else:
            cutoff = get_datetime(last_update)

        exists = frappe.db.exists("Instrument Profile", {"modified": [">", cutoff]})
        return {"has_updates": bool(exists)}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Instrument Profile API: check_pending_updates")
        return {"has_updates": False}
