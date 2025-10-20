"""
File: repair_portal/api/client_portal.py
Updated: 2025-07-13
Version: 1.4
Purpose: Secure API endpoints for client portal UI dashboard
"""

import frappe


@frappe.whitelist(allow_guest=False)
def get_my_instruments():
    """Return instrument list where the linked player belongs to the logged-in user."""
    client = frappe.db.get_value("Customer", {"linked_user": frappe.session.user}, "name")
    if not client:
        return []

    player_names = frappe.get_all("Player Profile", {"customer": client}, pluck="name")
    return frappe.get_all(
        "Instrument Profile",
        filters={"player_profile": ["in", player_names]},
        fields=["name", "instrument_type", "serial_no"],
    )


@frappe.whitelist(allow_guest=False)
def get_my_repairs():
    """Return recent Repair Orders linked to instruments owned by this client."""
    client = frappe.db.get_value("Customer", {"linked_user": frappe.session.user}, "name")
    if not client:
        return []

    player_names = frappe.get_all("Player Profile", {"customer": client}, pluck="name")
    if not player_names:
        return []

    instrument_names = frappe.get_all(
        "Instrument Profile", {"player_profile": ["in", player_names]}, pluck="name"
    )
    if not instrument_names:
        return []

    instrument_meta = {
        doc.name: doc
        for doc in frappe.get_all(
            "Instrument Profile",
            filters={"name": ["in", instrument_names]},
            fields=["name", "headline", "instrument_category", "serial_no"],
        )
    }

    repairs = frappe.get_all(
        "Repair Order",
        filters={
            "customer": client,
            "instrument_profile": ["in", instrument_names],
        },
        fields=[
            "name",
            "workflow_state",
            "instrument_profile",
            "priority",
            "target_delivery",
            "modified",
        ],
        order_by="modified desc",
        limit=10,
    )

    for entry in repairs:
        instrument = instrument_meta.get(entry.instrument_profile)
        if instrument:
            parts = [instrument.headline, instrument.instrument_category, instrument.serial_no]
            entry["instrument_label"] = " • ".join(filter(None, parts)) or instrument.name
        else:
            entry["instrument_label"] = entry.instrument_profile

    return repairs
