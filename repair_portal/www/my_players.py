import frappe

def get_context(context):
    user = frappe.session.user
    client = frappe.db.get_value("Client Profile", {"linked_user": user}, "name")

    filters = {"client_profile": client} if client else {"owner": user}

    context.title = "My Players"
    context.introduction = "Clarinet players connected to your studio or repair profile."
    context.players = frappe.get_all("Player Profile", filters=filters, fields=[
        "name", "player_name", "style_preferences", "tonal_goals", "route", "creation"
    ], order_by="creation desc")