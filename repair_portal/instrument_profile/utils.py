# File: repair_portal/instrument_profile/utils.py
# Updated: 2025-07-12
# Version: 1.0
# Purpose: Helper utilities for Instrument Profile module.

from __future__ import annotations

import frappe


def get_instrument_timeline(name: str) -> list[dict]:
    """Return ordered list of events for the given instrument."""
    doc = frappe.get_doc("Instrument Profile", name)
    events = []

    # manual events table
    for ev in doc.instrument_events:
        events.append(
            {
                "date": ev.date,
                "event_type": ev.event_type,
                "description": ev.description,
                "photo": ev.photo,
                "reference_link": ev.reference_link,
            }
        )

    # repair orders
    repair_orders = frappe.get_all(
        "Repair Order",
        filters={"instrument_profile": name},
        fields=["name", "status", "modified"],
    )
    for ro in repair_orders:
        events.append(
            {
                "date": ro.modified,
                "event_type": "Repair",
                "description": f"Repair Order {ro.name} - {ro.status}",
                "reference_link": f"/app/repair-order/{ro.name}",
            }
        )

    # repair task logs
    task_logs = frappe.db.get_all(
        "Repair Task Log",
        fields=["timestamp", "log_entry", "parent"],
        order_by="timestamp asc",
    )
    for log in task_logs:
        parent_repair = frappe.db.get_value("Repair Task", log.parent, "parent")
        instrument = frappe.db.get_value("Repair Order", parent_repair, "instrument_profile")
        if instrument == name:
            events.append(
                {
                    "date": log.timestamp,
                    "event_type": "Repair Task",
                    "description": log.log_entry,
                    "reference_link": f"/app/repair-task/{log.parent}",
                }
            )

    # photos
    photos = frappe.db.get_all("Image Log Entry", fields=["image", "comment", "parent", "creation"])
    for photo in photos:
        task_parent = frappe.db.get_value("Repair Task", photo.parent, "parent")
        inst = frappe.db.get_value("Repair Order", task_parent, "instrument_profile")
        if inst == name:
            events.append(
                {
                    "date": photo.creation,
                    "event_type": "Photo",
                    "description": photo.comment,
                    "photo": photo.image,
                    "reference_link": f"/app/repair-task/{photo.parent}",
                }
            )

    # player comments
    comments = frappe.get_all(
        "Instrument Comment",
        filters={"instrument_profile": name},
        fields=["comment", "creation"],
    )
    for cm in comments:
        events.append(
            {
                "date": cm.creation,
                "event_type": "Comment",
                "description": cm.comment,
                "reference_link": None,
            }
        )

    return sorted(events, key=lambda x: x["date"])
