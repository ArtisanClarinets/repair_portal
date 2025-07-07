# File Header Template
# Relative Path: repair_portal/www/instrument_profile.py
# Last Updated: 2025-07-06
# Version: v1.2
# Purpose: Fetches instrument profile data ensuring ownership validation with fallback to owner
# Dependencies: Instrument Profile, Player Profile, Client Profile, Customer, File

import frappe
from frappe import _

def get_context(context):
    """
    Prepares context for the Instrument Profile web page with customer ownership validation
    and fallback to Instrument owner if no Player Profile is linked.

    Args:
        context (dict): Frappe context dictionary.
    
    Returns:
        dict: Updated context with instrument data, service history, and related documents.
    """
    serial_no = frappe.form_dict.get("serial_no")
    if not serial_no:
        frappe.throw(_("Serial number is required."))

    try:
        instrument = frappe.get_doc("Instrument Profile", {"serial_number": serial_no})
    except frappe.DoesNotExistError:
        frappe.throw(_("Instrument with serial number {0} not found.").format(serial_no))
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Instrument Profile Fetch Error")
        frappe.throw(_("An unexpected error occurred while fetching the instrument profile."))

    # Determine customer ownership
    customer = None
    if instrument.player_profile:
        # Trace via Player Profile and Client Profile
        player_profile = frappe.get_doc("Player Profile", instrument.player_profile)

        if not player_profile.client_profile:
            frappe.throw(_("Player Profile {0} is not linked to a Client Profile.").format(player_profile.name))

        client_profile = frappe.get_doc("Client Profile", player_profile.client_profile)

        if not client_profile.customer:
            frappe.throw(_("Client Profile {0} is not linked to a Customer.").format(client_profile.name))

        customer = client_profile.customer

    elif instrument.owner:
        # Fallback: use direct Customer link
        customer = instrument.owner

    else:
        frappe.throw(_("This instrument is not linked to any Player Profile or Owner."))

    # Validate that logged-in user has access
    user = frappe.session.user

    if user == "Guest":
        frappe.throw(_("You must be logged in to view this instrument profile."))

    linked_contacts = frappe.get_all(
        "Contact",
        filters={"email_id": user},
        fields=["name"],
    )

    if not linked_contacts:
        frappe.throw(_("Your user account is not linked to any Customer record. Access denied."))

    # Check whether the Contact is linked to the correct Customer
    has_access = False
    for contact in linked_contacts:
        contact_links = frappe.get_all(
            "Dynamic Link",
            filters={
                "link_doctype": "Customer",
                "link_name": customer,
                "parenttype": "Contact",
                "parent": contact.name,
            }
        )
        if contact_links:
            has_access = True
            break

    if not has_access:
        frappe.throw(_("You do not have permission to view this instrument profile."))

    # Fetch Service History
    service_history = frappe.get_all(
        "Instrument Service Record",
        filters={"instrument": instrument.name},
        fields=["service_type", "service_date", "notes"],
        order_by="service_date desc"
    )

    # Fetch Documents
    documents = frappe.get_all(
        "File",
        filters={
            "attached_to_doctype": "Instrument Profile",
            "attached_to_name": instrument.name
        },
        fields=["file_url as url", "file_name as title"]
    )

    context.instrument = instrument
    context.service_history = service_history
    context.documents = documents

    return context
