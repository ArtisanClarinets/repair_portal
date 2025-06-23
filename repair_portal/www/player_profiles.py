"""Public listing of all player profiles."""

import frappe


def get_context(context):
    """Return context for /player_profiles."""
    context.title = "Player Profiles"
    context.player_profiles = frappe.get_all(
        "Player Profile",
        fields=[
            "name",
            "player_name",
            "style_preferences",
            "tonal_goals",
            "tech_notes",
            "client_profile",
        ],
    )
    if not context.player_profiles:
        context.empty_message = "No player profiles found."
    return context
