"""Deposit collection timing metrics."""
from __future__ import annotations

from typing import Any, Dict, List

import frappe
from frappe import _
from frappe.utils import get_datetime, time_diff_in_hours


def execute(filters: Dict[str, Any] | None = None) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    columns = [
        {"label": _("Estimate"), "fieldname": "name", "fieldtype": "Link", "options": "Repair Estimate", "width": 160},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": _("Deposit Amount"), "fieldname": "deposit_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Sent On"), "fieldname": "sent_on", "fieldtype": "Datetime", "width": 160},
        {"label": _("Approved On"), "fieldname": "approved_on", "fieldtype": "Datetime", "width": 160},
        {"label": _("Hours to Approval"), "fieldname": "hours_to_approve", "fieldtype": "Float", "width": 140},
    ]
    rows = []
    estimates = frappe.get_all(
        "Repair Estimate",
        filters={"approved_on": ("is", "set")},
        fields=["name", "customer", "deposit_amount", "sent_on", "approved_on"],
        order_by="approved_on desc",
        limit_page_length=200,
    )
    for estimate in estimates:
        sent = get_datetime(estimate.sent_on) if estimate.sent_on else None
        approved = get_datetime(estimate.approved_on) if estimate.approved_on else None
        hours = time_diff_in_hours(approved, sent) if sent and approved else None
        rows.append(
            {
                "name": estimate.name,
                "customer": estimate.customer,
                "deposit_amount": estimate.deposit_amount,
                "sent_on": estimate.sent_on,
                "approved_on": estimate.approved_on,
                "hours_to_approve": hours,
            }
        )
    return columns, rows

