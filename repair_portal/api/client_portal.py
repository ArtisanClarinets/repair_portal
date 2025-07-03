import frappe
from frappe import _
from frappe.utils import get_url


@frappe.whitelist()
def get_client_portal_data(client_profile_name):
    """
    Fetches all data needed for the client portal page.
    """
    if not frappe.db.exists("Client Profile", client_profile_name):
        frappe.throw(_("Client Profile not found"), frappe.DoesNotExistError)

    # Check permissions
    # This ensures that only the linked user or a user with system manager/admin rights can view the data.
    client_profile = frappe.get_doc("Client Profile", client_profile_name)
    if frappe.session.user not in ['Administrator', 'System Manager'] and client_profile.get("linked_user") != frappe.session.user:
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