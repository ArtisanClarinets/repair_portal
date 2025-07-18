import frappe
from frappe import _


@frappe.whitelist()
def get_profiles():
    """Return client, player, and instrument profiles for the logged-in user."""
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Login required"), frappe.PermissionError)

    client = frappe.db.get_value("Client Profile", {"linked_user": user}, "*", as_dict=True)
    if not client:
        return {"client": None, "players": [], "instruments": []}

    players = frappe.get_all(
        "Player Profile",
        filters={"client_profile": client.name},
        fields=["name", "player_name"],
    )
    player_names = [p.name for p in players]

    instruments = []
    if player_names:
        instruments = frappe.get_all(
            "Instrument Profile",
            filters={"player_profile": ["in", player_names]},
            fields=["name", "serial_no"],
        )

    return {"client": client, "players": players, "instruments": instruments}


@frappe.whitelist()
def save_profile(docname, data):
    """Update a document owned by the user after permission check."""
    if isinstance(data, str):
        data = frappe.parse_json(data)

    doc = frappe.get_doc(docname)
    if not frappe.has_permission(doc.doctype, ptype="write", doc=docname):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    doc.update(data)
    doc.save()
    return {"name": doc.name}
