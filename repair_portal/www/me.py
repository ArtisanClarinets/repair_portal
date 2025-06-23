"""Client profile dashboard for the logged-in user."""

# File: repair_portal/www/me.py
# Updated: 2025-07-10
# Version: 1.0
# Purpose: Display client profile details with linked players and instruments.

from __future__ import annotations

import frappe

login_required = True


def get_context(context):
    """Build context for /me route."""
    user = frappe.session.user
    client = frappe.get_doc("Client Profile", {"linked_user": user})

    instruments = frappe.get_all(
        "Instrument Profile",
        filters={"client_profile": client.name},
        fields=["name", "instrument_name", "serial_number", "route"],
        order_by="creation desc",
    )

    players = frappe.get_all(
        "Player Profile",
        filters={"client_profile": client.name},
        fields=["name", "player_name", "route"],
        order_by="creation desc",
    )

    context.profile = client
    context.consent_log = client.get("consent_log")
    context.instruments = instruments
    context.players = players
    context.title = client.client_name
    return context
