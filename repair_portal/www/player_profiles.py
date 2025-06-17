import frappe

def get_context(context):
    context.player_profiles = frappe.get_all("Player Profile", fields=[
        "name", "player_name", "style_preferences", "tonal_goals", "tech_notes", "client_profile"
    ])