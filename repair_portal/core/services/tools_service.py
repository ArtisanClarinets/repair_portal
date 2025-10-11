"""Technician tooling helper service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Mapping

from ..registry import Role
from ..security import rate_limited, require_roles

try:
    import frappe
except ImportError:  # pragma: no cover
    frappe = None  # type: ignore

LOGGER_NAME = "repair_portal.tools"


def _log(message: str, **context: object) -> None:
    if frappe is not None:
        frappe.logger(LOGGER_NAME).info(message, **context)


@require_roles(Role.TECHNICIAN, Role.REPAIR_MANAGER)
@rate_limited("tools-usage", limit=300, window_seconds=60)
def log_tool_usage(payload: Mapping[str, object]) -> Mapping[str, object]:
    """Persist a tool usage log with calibration checks."""

    if frappe is not None:
        record = dict(payload)
        record.setdefault("doctype", "Tool Usage Log")
        record.setdefault("logged_on", datetime.now(timezone.utc))
        doc = frappe.get_doc(record)
        doc.flags.ignore_permissions = True
        doc.insert()
        tool = record.get("tool")
        if tool:
            calibration_due = frappe.db.get_value("Tool", tool, "calibration_due_date")
            if calibration_due and calibration_due < datetime.now(timezone.utc).date():
                frappe.log_error(
                    "Tool calibration expired",
                    frappe.as_json({"tool": tool, "calibration_due": str(calibration_due)}),
                )
    _log("Tool usage logged", **dict(payload))
    return payload
