from __future__ import annotations

from collections import defaultdict
import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate


def execute(filters: dict | None = None):
    filters = filters or {}
    days = int(filters.get("days") or 7)
    start = getdate(add_days(nowdate(), -days + 1))

    availability = frappe.db.get_all(
        "Technician Availability",
        filters={"date": (">=", start)},
        fields=["technician", "date", "available_minutes"],
    )
    available_by_tech = defaultdict(int)
    for row in availability:
        available_by_tech[row.technician] += row.available_minutes or 0

    orders = frappe.db.get_all(
        "Repair Order",
        filters={
            "technician": ("is", "set"),
            "workflow_state": ("in", ["In Progress", "QC", "Ready to Ship", "Approved"]),
            "modified": (">=", start),
        },
        fields=["technician", "planned_hours", "name"],
    )
    planned_by_tech = defaultdict(float)
    for row in orders:
        planned_by_tech[row.technician] += float(row.planned_hours or 0) * 60.0

    columns = [
        {"label": _("Technician"), "fieldname": "technician", "fieldtype": "Link", "options": "User", "width": 160},
        {"label": _("Planned Minutes"), "fieldname": "planned", "fieldtype": "Float", "width": 140},
        {"label": _("Available Minutes"), "fieldname": "available", "fieldtype": "Float", "width": 140},
        {"label": _("Utilization %"), "fieldname": "utilization", "fieldtype": "Percent", "width": 130},
        {"label": _("Risk"), "fieldname": "risk", "fieldtype": "Data", "width": 100},
    ]

    data = []
    for technician in sorted(set(list(available_by_tech.keys()) + list(planned_by_tech.keys()))):
        available = float(available_by_tech.get(technician) or 0)
        planned = float(planned_by_tech.get(technician) or 0)
        utilization = 0.0
        risk = "Low"
        if available > 0:
            utilization = (planned / available) * 100.0
            if utilization > 100:
                risk = "High"
            elif utilization > 75:
                risk = "Medium"
        elif planned > 0:
            utilization = 100.0
            risk = "High"
        data.append(
            {
                "technician": technician,
                "planned": round(planned, 2),
                "available": round(available, 2),
                "utilization": round(utilization, 2),
                "risk": risk,
            }
        )

    chart = {
        "data": {
            "labels": [row["technician"] for row in data],
            "datasets": [
                {
                    "name": _("Utilization %"),
                    "values": [row["utilization"] for row in data],
                }
            ],
        },
        "type": "percentage",
    }

    return columns, data, None, chart
