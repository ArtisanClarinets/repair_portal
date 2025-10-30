"""Utilities for portal access control."""

from __future__ import annotations

from typing import List, Sequence

import frappe
from frappe import _


def customers_for_user(user: str) -> Sequence[str]:
    """Return the customer records linked to the given user."""

    links: List[str] = []
    contacts = frappe.get_all("Contact", filters={"user": user}, pluck="name")
    if contacts:
        links.extend(
            frappe.get_all(
                "Dynamic Link",
                filters={
                    "parenttype": "Contact",
                    "parent": ["in", contacts],
                    "link_doctype": "Customer",
                },
                pluck="link_name",
            )
        )
    direct_customer = frappe.db.get_value("Customer", {"portal_user": user}, "name")
    if direct_customer:
        links.append(direct_customer)
    return list({link for link in links if link})


def ensure_customer_access(customer: str | None, user: str) -> None:
    """Raise PermissionError if ``user`` is not allowed to access ``customer`` records."""

    if not customer:
        frappe.throw(_("Missing customer association"), frappe.PermissionError)
    allowed = customers_for_user(user)
    if customer not in allowed:
        frappe.throw(_("Not permitted"), frappe.PermissionError)
