"""Service plan attach and claim metrics."""
from __future__ import annotations

from typing import Any, Dict, List

import frappe
from frappe import _


def execute(filters: Dict[str, Any] | None = None) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    columns = [
        {"label": _("Metric"), "fieldname": "metric", "fieldtype": "Data", "width": 240},
        {"label": _("Value"), "fieldname": "value", "fieldtype": "Float", "width": 120}
    ]
    enrollments = frappe.db.count("Service Plan Enrollment")
    active = frappe.db.count("Service Plan Enrollment", {"status": "Active"})
    claims = frappe.db.count("Warranty Claim")
    approved_claims = frappe.db.count("Warranty Claim", {"claim_status": ("in", ["Approved", "Fulfilled"] )})
    instrument_count = frappe.db.count("Instrument")
    attach_rate = (active / instrument_count * 100.0) if instrument_count else 0.0
    claim_rate = (approved_claims / active * 100.0) if active else 0.0
    data = [
        {"metric": _("Enrollments"), "value": enrollments},
        {"metric": _("Active Enrollments"), "value": active},
        {"metric": _("Warranty Claims"), "value": claims},
        {"metric": _("Approved Claims"), "value": approved_claims},
        {"metric": _("Attach Rate %"), "value": attach_rate},
        {"metric": _("Claim Rate %"), "value": claim_rate},
    ]
    return columns, data

