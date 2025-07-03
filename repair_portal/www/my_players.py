"""
File: repair_portal/www/my_players.py
Updated: 2025-07-03
Version: 1.1
Purpose: List clarinet players linked to the logged-in user. Ensures login is required for access.
"""

import frappe

login_required = True

def get_context(context):
    """Build page context for /my_players."""
    user = frappe.session.user
    client = frappe.db.get_value("Client Profile", {"linked_user": user}, "name")

    filters = {"client_profile": client} if client else {"owner": user}

    context.title = "My Players"
    context.introduction = "Clarinet players connected to your studio or repair profile."
    context.players = frappe.get_all(
        "Player Profile",
        filters=filters,
        fields=[
            "name",
            "player_name",
            "style_preferences",
            "tonal_goals",
            "route",
            "creation",
        ],
        order_by="creation desc",
    )

    if not context.players:
        context.empty_message = "No players found for your profile."
    return context
