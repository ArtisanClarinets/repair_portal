"""Permission logic for Instrument."""
from __future__ import annotations

import frappe

STAFF_ROLES = {"Owner/Admin", "Front Desk", "Repair Technician", "Inventory", "Accounting"}


def has_permission(doc, ptype: str, user: str | None = None) -> bool:
    user = user or frappe.session.user
    if user == "Guest":
        return False
    if set(frappe.get_roles(user)) & STAFF_ROLES:
        return True
    if frappe.has_role(user, "Customer") and ptype in {"read"}:
        return _is_customer_owner(doc.customer, user)
    if frappe.has_role(user, "School/Teacher") and ptype in {"read"}:
        return _is_school_contact(doc.customer, user)
    return False


def _is_customer_owner(customer: str, user: str) -> bool:
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
                "link_name": customer,
            },
        )
    )


def _is_school_contact(customer: str, user: str) -> bool:
    school_flag = frappe.db.get_value("Customer", customer, "is_school")
    if not school_flag:
        return False
    return _is_customer_owner(customer, user)

