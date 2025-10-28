"""Rental utilization metrics."""
from __future__ import annotations

from typing import Any, Dict, List

import frappe
from frappe import _


def execute(filters: Dict[str, Any] | None = None) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    columns = [
        {"label": _("Metric"), "fieldname": "metric", "fieldtype": "Data", "width": 240},
        {"label": _("Value"), "fieldname": "value", "fieldtype": "Float", "width": 120}
    ]
    total = frappe.db.count("Rental Contract")
    active = frappe.db.count("Rental Contract", {"status": ("in", ["Active", "Overdue"] )})
    returned = frappe.db.count("Rental Contract", {"status": "Returned"})
    utilization = (active / total * 100.0) if total else 0.0
    data = [
        {"metric": _("Active Rentals"), "value": active},
        {"metric": _("Returned Rentals"), "value": returned},
        {"metric": _("Total Contracts"), "value": total},
        {"metric": _("Utilization %"), "value": utilization},
    ]
    return columns, data

