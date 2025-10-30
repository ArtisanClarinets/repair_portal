"""Customer-facing repair status tracker."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

import frappe
from frappe import _
from frappe.utils import format_datetime, get_datetime
from werkzeug.exceptions import NotFound

from repair_portal.repair_portal.utils import token as token_utils


def get_context(context: Dict[str, Any]) -> Dict[str, Any]:
    token = frappe.form_dict.get("portal_token") or frappe.form_dict.get("name")
    if not token:
        raise NotFound()
    hashed = token_utils.hash_token(token, "repair-request")
    request_name = frappe.db.get_value("Repair Request", {"portal_token": hashed}, "name")
    if not request_name:
        raise NotFound()
    repair_request = frappe.get_doc("Repair Request", request_name)
    mail_in_name = frappe.db.get_value("Mail In Repair Request", {"repair_request": request_name}, "name")
    mail_in = frappe.get_doc("Mail In Repair Request", mail_in_name) if mail_in_name else None
    orders = frappe.get_all(
        "Repair Order",
        filters={"repair_request": request_name},
        fields=["name", "workflow_state", "technician", "bench", "planned_hours", "creation", "modified"],
        order_by="creation asc",
    )
    timeline = _build_timeline(repair_request, mail_in, orders)
    context.update(
        {
            "no_cache": 1,
            "show_sidebar": False,
            "title": _("Repair Status"),
            "portal_token": token,
            "repair_request": repair_request,
            "mail_in_request": mail_in,
            "repair_orders": orders,
            "timeline": timeline,
        }
    )
    return context


def _build_timeline(repair_request, mail_in, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    events.append(
        {
            "timestamp": repair_request.creation,
            "display_ts": format_datetime(repair_request.creation),
            "title": _("Repair request submitted"),
            "body": repair_request.requested_services,
        }
    )
    if mail_in:
        events.append(
            {
                "timestamp": mail_in.creation,
                "display_ts": format_datetime(mail_in.creation),
                "title": _("Mail-in request created"),
                "body": _(f"Carrier preference: {mail_in.carrier or 'TBD'}"),
            }
        )
        if mail_in.status:
            events.append(
                {
                    "timestamp": mail_in.modified,
                    "display_ts": format_datetime(mail_in.modified),
                    "title": _(f"Mail-in status: {mail_in.status}"),
                    "body": mail_in.arrival_condition_notes or "",
                }
            )
        for shipment in (mail_in.get("shipments") or []):
            ts: datetime = getattr(shipment, "creation", None) or mail_in.modified or mail_in.creation
            events.append(
                {
                    "timestamp": ts,
                    "display_ts": format_datetime(ts),
                    "title": _(f"Shipment {shipment.direction}"),
                    "body": _(f"{shipment.carrier or ''} {shipment.tracking_no or ''}"),
                }
            )
    for order in orders:
        ts = order.get("creation") or get_datetime()
        events.append(
            {
                "timestamp": ts,
                "display_ts": format_datetime(ts),
                "title": _(f"Repair Order {order['name']}"),
                "body": _(f"Current stage: {order['workflow_state'] or 'Requested'}"),
            }
        )
    events.sort(key=lambda entry: entry["timestamp"] or get_datetime())
    return events
