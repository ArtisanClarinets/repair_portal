import frappe


def get_context(context):
    user = frappe.session.user

    if user == "Guest":
        frappe.throw("You must be logged in to view this page.")

    # Extract the name from the route kwargs
    player_name = context.route.split("/")[-1]

    # Try to load the record
    player = frappe.db.get("Player Profile", {"name": player_name})

    if not player:
        return {"not_found": True, "title": "Player Profile"}

    # Verify that this profile belongs to this user's Client Profile
    client_profile = frappe.db.get_value("Client Profile", {"linked_user": user}, "name")

    if not client_profile or player.client_profile != client_profile:
        return {"unauthorized": True, "title": "Player Profile"}

    return {
        "profile": frappe.get_doc("Player Profile", player_name),
        "title": f"Player Profile – {player.player_name}",
    }
