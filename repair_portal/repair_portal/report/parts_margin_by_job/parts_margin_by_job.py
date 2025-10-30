from __future__ import annotations

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters: dict | None = None):
    filters = filters or {}
    states = tuple(filters.get("states") or ["Completed", "Ready to Ship", "QC"])
    orders = frappe.db.get_all(
        "Repair Order",
        filters={"workflow_state": ("in", states)},
        fields=["name", "customer", "repair_class"],
    )
    if not orders:
        return _columns(), [], None, None

    order_names = [row.name for row in orders]
    cost_map = defaultdict(float)
    actual_rows = frappe.db.get_all(
        "Actual Material",
        filters={"parent": ("in", order_names)},
        fields=["parent", "qty", "valuation_rate"],
    )
    for row in actual_rows:
        cost_map[row.parent] += flt(row.qty) * flt(row.valuation_rate)

    revenue_map = defaultdict(float)
    estimates = frappe.db.get_all(
        "Repair Estimate",
        filters={"repair_order": ("in", order_names)},
        fields=["name", "repair_order"],
    )
    estimate_map = {row.name: row.repair_order for row in estimates}
    if estimate_map:
        upsells = frappe.db.get_all(
            "Estimate Upsell",
            filters={"parent": ("in", list(estimate_map.keys())), "accepted": 1},
            fields=["parent", "price"],
        )
        for row in upsells:
            order_name = estimate_map.get(row.parent)
            if order_name:
                revenue_map[order_name] += flt(row.price)

    data = []
    for order in orders:
        revenue = revenue_map.get(order.name, 0.0)
        cost = cost_map.get(order.name, 0.0)
        margin = revenue - cost
        margin_pct = (margin / revenue * 100.0) if revenue else 0.0
        data.append(
            {
                "repair_order": order.name,
                "repair_class": order.repair_class or "-",
                "customer": order.customer,
                "parts_revenue": round(revenue, 2),
                "parts_cost": round(cost, 2),
                "margin": round(margin, 2),
                "margin_pct": round(margin_pct, 2),
            }
        )

    chart = {
        "data": {
            "labels": [row["repair_order"] for row in data],
            "datasets": [
                {
                    "name": _("Margin"),
                    "values": [row["margin"] for row in data],
                }
            ],
        },
        "type": "bar",
    }

    return _columns(), data, None, chart


def _columns():
    return [
        {"label": _("Repair Order"), "fieldname": "repair_order", "fieldtype": "Link", "options": "Repair Order", "width": 140},
        {"label": _("Repair Class"), "fieldname": "repair_class", "fieldtype": "Data", "width": 140},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 160},
        {"label": _("Parts Revenue"), "fieldname": "parts_revenue", "fieldtype": "Currency", "width": 140},
        {"label": _("Parts Cost"), "fieldname": "parts_cost", "fieldtype": "Currency", "width": 140},
        {"label": _("Margin"), "fieldname": "margin", "fieldtype": "Currency", "width": 120},
        {"label": _("Margin %"), "fieldname": "margin_pct", "fieldtype": "Percent", "width": 100},
    ]
