"""
File: repair_portal/api/client_portal.py
Updated: 2025-07-03
Version: 1.1
Purpose: Secure API endpoint for client portal, restricts guest access, and documents usage. 
"""
import frappe
from frappe import _


@frappe.whitelist(allow_guest=False)
def get_client_portal_data(client_profile_name):
    """
    Fetches all data needed for the client portal page. Only accessible to owner or admin.
    """
    if not frappe.db.exists("Client Profile", client_profile_name):
        frappe.throw(_("Client Profile not found"), frappe.DoesNotExistError)

    # Check permissions
    # Only linked user or admin/system manager may view data.
    client_profile = frappe.get_doc("Client Profile", client_profile_name)
    if (
        frappe.session.user not in ["Administrator", "System Manager"]
        and client_profile.get("linked_user") != frappe.session.user
    ):
        frappe.throw(_("You are not authorized to view this profile."), frappe.PermissionError)

    # Fetch Player Profiles
    players = frappe.get_all(
        "Player Profile",
        filters={"client_profile": client_profile_name},
        fields=["name", "player_name", "profile_picture", "route"],
    )

    # Fetch Instrument Profiles
    instruments = frappe.get_all(
        "Instrument Profile",
        filters={"client_profile": client_profile_name},
        fields=["name", "instrument_name", "serial_number", "instrument_image", "route"],
    )

    return {
        "client_info": client_profile,
        "player_profiles": players,
        "instrument_profiles": instruments,
    }
