"""Mail-in repair SLA metrics."""
from __future__ import annotations

from typing import Any, Dict, List

import frappe
from frappe import _
from frappe.utils import get_datetime, time_diff_in_hours


def execute(filters: Dict[str, Any] | None = None) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    columns = [
        {"label": _("Request"), "fieldname": "name", "fieldtype": "Link", "options": "Mail In Repair Request", "width": 160},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": _("Created"), "fieldname": "creation", "fieldtype": "Datetime", "width": 160},
        {"label": _("Last Updated"), "fieldname": "modified", "fieldtype": "Datetime", "width": 160},
        {"label": _("Hours Open"), "fieldname": "hours_open", "fieldtype": "Float", "width": 120}
    ]
    records = frappe.get_all(
        "Mail In Repair Request",
        filters={},
        fields=["name", "customer", "status", "creation", "modified"],
        order_by="creation desc",
        limit_page_length=200,
    )
    data = []
    now = get_datetime()
    for row in records:
        creation = get_datetime(row.creation) if row.creation else None
        last_update = get_datetime(row.modified) if row.modified else None
        end = last_update if row.status in {"Checked-In", "Closed"} else now
        hours_open = time_diff_in_hours(end, creation) if creation else None
        data.append(
            {
                "name": row.name,
                "customer": row.customer,
                "status": row.status,
                "creation": row.creation,
                "modified": row.modified,
                "hours_open": hours_open,
            }
        )
    return columns, data

