"""
File: repair_portal/www/player_profiles.py
Updated: 2025-07-03
Version: 1.1
Purpose: Public listing of player profiles. Sanitizes fields for public view, adds header, and restricts to published profiles only.
"""

import frappe


def get_context(context):
    """Return context for /player_profiles."""
    context.title = "Player Profiles"
    context.header = "Public Clarinet Player Directory"
    context.player_profiles = frappe.get_all(
        "Player Profile",
        filters={"published": 1},
        fields=[
            "name",
            "player_name",
            "style_preferences",
            "tonal_goals",
        ],
    )
    if not context.player_profiles:
        context.empty_message = "No player profiles found."
    return context
