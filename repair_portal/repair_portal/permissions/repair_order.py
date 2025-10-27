"""Portal permission checks for Repair Order."""
from __future__ import annotations

import frappe

from repair_portal.repair_portal.utils import token as token_utils

ALLOWED_ROLES = {"Owner/Admin", "Front Desk", "Repair Technician", "Inventory", "Accounting"}


def has_permission(doc, ptype: str, user: str | None = None) -> bool:
    user = user or frappe.session.user
    if user == "Guest":
        return _guest_can_read(doc, ptype)
    if set(frappe.get_roles(user)) & ALLOWED_ROLES:
        return True
    if frappe.has_role(user, "Customer") and ptype in {"read"}:
        return _user_matches_customer(doc, user)
    return False


def _guest_can_read(doc, ptype: str) -> bool:
    if ptype not in {"read"}:
        return False
    token = frappe.form_dict.get("portal_token") or frappe.form_dict.get("token")
    if not token:
        return False
    hashed = token_utils.hash_token(token, "repair-request")
    return bool(frappe.db.exists("Repair Request", {"name": doc.repair_request, "portal_token": hashed}))


def _user_matches_customer(doc, user: str) -> bool:
    contact = frappe.db.get_value("Contact", {"user": user}, "name")
    if not contact:
        return False
    return bool(
        frappe.db.exists(
            "Dynamic Link",
            {
                "parent": contact,
                "parenttype": "Contact",
                "link_doctype": "Customer",
                "link_name": doc.customer,
            },
        )
    )
