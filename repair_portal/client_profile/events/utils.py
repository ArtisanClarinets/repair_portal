# ---------------------------------------------------------------------------
# File: repair_portal/client_profile/events/utils.py
# Updated: 2025-06-29
# Version: v1.1
# Purpose: Auto-create Client Profile when a new User is inserted.
# Notes: Hooks User.after_insert
# ---------------------------------------------------------------------------

import frappe


def create_client_profile(doc, method=None):
    """
    Create a Client Profile as soon as a User record is created.

    Args:
        doc (frappe.model.document.Document): The newly-inserted User doc
        method: (ignored, added for hook signature compatibility)
    """

    if frappe.db.exists("Client Profile", {"linked_user": doc.name}):
        return

    email = doc.email
    customer = None
    if email:
        customer = frappe.db.get_value(
            "Customer",
            {"email_id": email},
            ["name", "customer_name"],
            as_dict=True,
        )

    try:
        profile = frappe.get_doc(
            {
                "doctype": "Client Profile",
                "linked_user": doc.name,
                "client_name": doc.full_name or doc.first_name or "Unnamed",
                "email": email,
                "customer": customer.name if customer else None,
            }
        )

        profile.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "ClientProfile Auto-Creation Failed")
