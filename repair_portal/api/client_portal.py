"""
File: repair_portal/api/client_portal.py
Updated: 2025-07-06
Version: 1.3
Purpose: Secure API endpoint for client portal. Returns all related records while validating ownership.
"""

import frappe
from frappe import _


@frappe.whitelist(allow_guest=False)
def get_client_portal_data(client_profile_name):
    """
    Fetches all data needed for the client portal page.
    Only accessible to the linked user, Administrator, or System Manager.
    """
    if not frappe.db.exists("Client Profile", client_profile_name):
        frappe.throw(_("Client Profile not found"), frappe.DoesNotExistError)

    # Load Client Profile Doc
    client_profile = frappe.get_doc("Client Profile", client_profile_name)

    # Permission check
    if (
        frappe.session.user != "Administrator"
        and not frappe.has_role("System Manager")
        and client_profile.get("linked_user") != frappe.session.user
    ):
        frappe.throw(_("You are not authorized to view this profile."), frappe.PermissionError)

    # Player Profiles linked to this Client Profile
    players = frappe.get_all(
        "Player Profile",
        filters={"client_profile": client_profile_name},
        fields=["name", "player_name", "profile_picture"]
    )

    # Instrument Profiles linked to those Player Profiles
    instrument_filters = {}
    if players:
        instrument_filters["player_profile"] = ["in", [p["name"] for p in players]]

    instruments = []
    if instrument_filters:
        instruments = frappe.get_all(
            "Instrument Profile",
            filters=instrument_filters,
            fields=["name", "instrument_name", "serial_number", "instrument_image"]
        )

    # Service Records linked to those Instruments
    service_records = []
    if instruments:
        service_records = frappe.get_all(
            "Instrument Service Record",
            filters={"instrument": ["in", [i["name"] for i in instruments]]},
            fields=[
                "name",
                "instrument",
                "service_type",
                "service_date",
                "notes"
            ],
            order_by="service_date desc",
            limit=10
        )

    # Files attached to those Instruments
    documents = []
    if instruments:
        documents = frappe.get_all(
            "File",
            filters={
                "attached_to_doctype": "Instrument Profile",
                "attached_to_name": ["in", [i["name"] for i in instruments]]
            },
            fields=[
                "file_url as url",
                "file_name as title",
                "attached_to_name as instrument"
            ]
        )

    return {
        "client_info": {
            "name": client_profile.name,
            "client_name": client_profile.client_name,
            "email": client_profile.email,
            "phone": client_profile.phone,
            "profile_image": client_profile.client_profile_image
        },
        "player_profiles": players,
        "instrument_profiles": instruments,
        "service_records": service_records,
        "documents": documents
    }
