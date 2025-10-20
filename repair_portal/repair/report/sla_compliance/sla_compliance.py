# Path: repair_portal/repair/report/sla_compliance/sla_compliance.py
# Script Report: SLA Compliance for Repair Orders

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import now_datetime

RO = "Repair Order"

# Preferred → fallback fieldnames we’ll try to read on Repair Order
FIELD_PREFS = {
    "service_type": ["service_type", "repair_type", "service_category"],
    "workshop": ["workshop"],
    "customer": ["customer"],
    "workflow_state": ["workflow_state"],
    "sla_policy": ["sla_policy"],
    "sla_start": ["sla_start"],
    "sla_due": ["sla_due"],
    "sla_progress_pct": ["sla_progress_pct"],
    "sla_status": ["sla_status"],
    "sla_breached": ["sla_breached"],
    "modified": ["modified"],
}


def execute(filters: dict[str, Any] | None = None) -> tuple[list[dict], list[list]]:
    filters = filters or {}
    columns = _get_columns()
    rows = _get_data(filters)
    return columns, rows


def _get_columns() -> list[dict[str, Any]]:
    return [
        {"label": "Repair Order", "fieldname": "name", "fieldtype": "Link", "options": RO, "width": 140},
        {"label": "Customer", "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
        {"label": "Service Type", "fieldname": "service_type", "fieldtype": "Data", "width": 140},
        {
            "label": "Workshop",
            "fieldname": "workshop",
            "fieldtype": "Link",
            "options": "Workshop",
            "width": 120,
        },
        {
            "label": "SLA Policy",
            "fieldname": "sla_policy",
            "fieldtype": "Link",
            "options": "SLA Policy",
            "width": 140,
        },
        {"label": "SLA Start", "fieldname": "sla_start", "fieldtype": "Datetime", "width": 160},
        {"label": "SLA Due", "fieldname": "sla_due", "fieldtype": "Datetime", "width": 160},
        {"label": "Progress (%)", "fieldname": "sla_progress_pct", "fieldtype": "Percent", "width": 110},
        {"label": "SLA Status", "fieldname": "sla_status", "fieldtype": "Data", "width": 110},
        {"label": "Breached", "fieldname": "sla_breached", "fieldtype": "Check", "width": 90},
        {"label": "Overdue (min)", "fieldname": "overdue_minutes", "fieldtype": "Int", "width": 120},
        {"label": "Workflow State", "fieldname": "workflow_state", "fieldtype": "Data", "width": 140},
        {"label": "Modified", "fieldname": "modified", "fieldtype": "Datetime", "width": 160},
    ]


def _get_data(filters: dict[str, Any]) -> list[dict[str, Any]]:
    meta = frappe.get_meta(RO)

    def exists(fieldname: str) -> bool:
        return fieldname == "name" or any(df.fieldname == fieldname for df in meta.fields)

    # Resolve which actual field to use for each logical key
    def pick(logical: str) -> str | None:
        for cand in FIELD_PREFS.get(logical, []):
            if exists(cand):
                return cand
        return None

    # Build SELECT fields list safely
    select_fields = ["name"]
    actual_map: dict[str, str | None] = {}
    for logical in FIELD_PREFS:
        actual = pick(logical)
        actual_map[logical] = actual
        if actual and actual not in select_fields:
            select_fields.append(actual)

    # Build filters, only on fields that exist
    where: dict[str, Any] = {"docstatus": ["<", 2]}

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    if from_date and to_date:
        where["modified"] = ["between", [f"{from_date} 00:00:00", f"{to_date} 23:59:59"]]
    elif from_date:
        where["modified"] = [">=", f"{from_date} 00:00:00"]
    elif to_date:
        where["modified"] = ["<=", f"{to_date} 23:59:59"]

    if filters.get("workshop") and actual_map["workshop"]:
        where[actual_map["workshop"]] = filters["workshop"]

    # Allow service_type filter even if actual field has a different name
    if filters.get("service_type"):
        svc_field = actual_map["service_type"]
        if svc_field:
            where[svc_field] = filters["service_type"]

    if filters.get("breached_only") and actual_map["sla_breached"]:
        where[actual_map["sla_breached"]] = 1

    # Query
    ros = frappe.get_all(
        RO,
        filters=where,
        fields=select_fields,
        order_by=f"{actual_map['sla_due'] or 'modified'} asc, modified desc",
    )

    # Bulk resolve customer display names (once per unique customer)
    customer_field = actual_map["customer"]
    customer_map: dict[str, str] = {}
    if customer_field:
        unique_customers = sorted({r.get(customer_field) for r in ros if r.get(customer_field)})
        if unique_customers:
            try:
                # Try to fetch Customer.customer_name (if present), fallback to name
                rows = frappe.get_all(
                    "Customer", filters={"name": ["in", unique_customers]}, fields=["name", "customer_name"]
                )
                for rr in rows:
                    display = rr.get("customer_name") or rr.get("name")
                    customer_map[rr["name"]] = display
            except Exception:
                for cname in unique_customers:
                    customer_map[cname] = cname

    now = now_datetime()
    out: list[dict[str, Any]] = []

    for r in ros:
        row: dict[str, Any] = {"name": r["name"]}

        # Map/alias fields into the report schema
        for logical in [
            "service_type",
            "workshop",
            "sla_policy",
            "sla_start",
            "sla_due",
            "sla_progress_pct",
            "sla_status",
            "sla_breached",
            "workflow_state",
            "modified",
        ]:
            actual = actual_map.get(logical)
            row[logical] = r.get(actual) if actual else None

        # Customer display value
        cust_val = r.get(customer_field) if customer_field else None
        row["customer_name"] = customer_map.get(cust_val or "", cust_val or "")

        # Overdue (min)
        overdue = 0
        if row.get("sla_due"):
            delta = now - row["sla_due"]
            overdue = int(delta.total_seconds() // 60) if delta.total_seconds() > 0 else 0
        row["overdue_minutes"] = overdue

        out.append(row)

    return out
