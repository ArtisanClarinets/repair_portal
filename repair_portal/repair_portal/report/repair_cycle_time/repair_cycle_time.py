from __future__ import annotations

import frappe
from frappe import _


def execute(filters: dict | None = None):
    filters = filters or {}
    states = tuple(filters.get("states") or ["Completed", "Ready to Ship"])
    placeholders = ",".join(["%s"] * len(states))
    results = frappe.db.sql(
        f"""
        SELECT
            coalesce(re.repair_class, 'Unclassified') AS repair_class,
            COUNT(ro.name) AS total_orders,
            AVG(TIMESTAMPDIFF(HOUR, ro.creation, ro.modified)) AS avg_hours,
            MIN(TIMESTAMPDIFF(HOUR, ro.creation, ro.modified)) AS min_hours,
            MAX(TIMESTAMPDIFF(HOUR, ro.creation, ro.modified)) AS max_hours
        FROM `tabRepair Order` ro
        LEFT JOIN `tabRepair Estimate` re ON re.repair_order = ro.name
        WHERE ro.workflow_state IN ({placeholders})
        GROUP BY repair_class
        ORDER BY avg_hours ASC
        """,
        states,
        as_dict=True,
    )

    columns = [
        {"label": _("Repair Class"), "fieldname": "repair_class", "fieldtype": "Data", "width": 200},
        {"label": _("Orders"), "fieldname": "total_orders", "fieldtype": "Int", "width": 90},
        {"label": _("Average Hours"), "fieldname": "avg_hours", "fieldtype": "Float", "width": 130},
        {"label": _("Fastest Hours"), "fieldname": "min_hours", "fieldtype": "Float", "width": 120},
        {"label": _("Slowest Hours"), "fieldname": "max_hours", "fieldtype": "Float", "width": 120},
    ]

    chart = {
        "data": {
            "labels": [row["repair_class"] for row in results],
            "datasets": [
                {
                    "name": _("Average Hours"),
                    "values": [round(row["avg_hours"] or 0, 2) for row in results],
                }
            ],
        },
        "type": "line",
    }

    for row in results:
        for key in ("avg_hours", "min_hours", "max_hours"):
            value = row.get(key)
            if value is not None:
                row[key] = round(value, 2)

    return columns, results, None, chart
