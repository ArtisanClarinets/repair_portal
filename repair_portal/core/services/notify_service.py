"""Notification helper service."""

from __future__ import annotations

from typing import Mapping

from ..contracts import message as message_contracts
from ..events import publish
from ..registry import EventTopic, Role
from ..security import rate_limited, require_roles

try:
    import frappe
except ImportError:  # pragma: no cover
    frappe = None  # type: ignore

LOGGER_NAME = "repair_portal.notify"


def _log(message: str, **context: object) -> None:
    if frappe is not None:
        frappe.logger(LOGGER_NAME).info(message, **context)


@require_roles(Role.CUSTOMER_SERVICE, Role.REPAIR_MANAGER)
@rate_limited("notify-send", limit=120, window_seconds=60)
def send_customer_message(payload: Mapping[str, object]) -> message_contracts.CustomerMessage:
    """Send a message to a customer and log the event."""

    message = message_contracts.CustomerMessage(**payload)
    _log("Customer message", repair_order=message.repair_order, recipient=message.recipient)
    if frappe is not None:
        doc = frappe.get_doc(
            {
                "doctype": "Repair Communication",
                "repair_order": message.repair_order,
                "subject": message.subject,
                "content": message.body,
                "sent_via": message.via,
                "visible_in_portal": message.visible_in_portal,
            }
        )
        doc.flags.ignore_permissions = True
        doc.insert()
    publish(EventTopic.CUSTOMER_MESSAGE_SENT, message.dict())
    return message


@require_roles(Role.REPAIR_MANAGER)
@rate_limited("notify-visibility", limit=60, window_seconds=60)
def toggle_portal_visibility(payload: Mapping[str, object]) -> message_contracts.PortalVisibility:
    """Toggle portal visibility for repair updates."""

    visibility = message_contracts.PortalVisibility(**payload)
    _log("Portal visibility toggled", repair_order=visibility.repair_order, visible=visibility.visible)
    if frappe is not None:
        frappe.db.set_value(
            "Repair Order",
            visibility.repair_order,
            {"show_portal_updates": visibility.visible, "portal_visibility_reason": visibility.reason},
        )
    return visibility
