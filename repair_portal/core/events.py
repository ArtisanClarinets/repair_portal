"""Shared event helpers for the repair_portal app."""

from __future__ import annotations

import json
from typing import Any, Mapping

from .registry import EventTopic, QueueName

try:
    import frappe
except ImportError:  # pragma: no cover - handled in unit tests via skip
    frappe = None  # type: ignore


def _serialize_payload(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, default=str, ensure_ascii=False)


def publish(topic: EventTopic | str, payload: Mapping[str, Any]) -> None:
    """Publish a structured event to the site event bus."""

    serialized = _serialize_payload(dict(payload))
    topic_value = topic.value if isinstance(topic, EventTopic) else topic

    if frappe is None:
        return

    frappe.logger().info("repair_portal.event", topic=topic_value, payload=serialized)
    frappe.enqueue(
        "frappe.event_streaming.doctype.event_update_log.event_update_log.process_event",
        queue=QueueName.REPAIR_NOTIFY.value,
        event=topic_value,
        payload=serialized,
        now=False,
    )
