import frappe


def get_context(context):
    user = frappe.session.user

    if user == "Guest":
        frappe.throw("You must be logged in to view this page.")

    client_profile_name = frappe.db.get_value("Client Profile", {"linked_user": user})

    if not client_profile_name:
        return {"no_profile": True, "title": "My Client Profile"}

    profile = frappe.get_doc("Client Profile", client_profile_name)

    players = frappe.get_all(
        "Player Profile",
        filters={"client_profile": profile.name},
        fields=["name", "player_name", "route", "published", "profile_status"],
    )

    return {"profile": profile, "players": players, "title": "My Client Profile"}
