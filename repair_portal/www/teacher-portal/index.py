"""Teacher and school dashboard portal."""
from __future__ import annotations

import frappe
from frappe import _

from repair_portal.repair_portal.utils.feature_flags import is_enabled

no_cache = 1


def get_context(context: dict) -> dict:
    if not is_enabled("enable_rentals"):
        frappe.throw(_("Rentals are disabled."), frappe.PermissionError)
    user = frappe.session.user
    if user == "Guest" or not frappe.has_role(user, "School/Teacher"):
        frappe.throw(_("Teacher access required."), frappe.PermissionError)
    customer = _resolve_school_customer(user)
    if not customer:
        frappe.throw(_("No school account linked to your profile."), frappe.PermissionError)
    context.update(
        {
            "page_title": _("Teacher Portal"),
            "school_customer": customer,
            "rentals": _fetch_rentals(customer),
            "quotes": _fetch_quotes(customer),
            "ready_repairs": _fetch_repairs(customer),
        }
    )
    return context


def _resolve_school_customer(user: str) -> str | None:
    contact = frappe.db.get_value("Contact", {"user": user}, "name")
    if not contact:
        return None
    links = frappe.db.get_all(
        "Dynamic Link",
        filters={
            "parenttype": "Contact",
            "parent": contact,
            "link_doctype": "Customer",
        },
        fields=["link_name"],
    )
    for row in links:
        if frappe.db.get_value("Customer", row.link_name, "is_school"):
            return row.link_name
    return None


def _fetch_rentals(customer: str) -> list[dict]:
    return frappe.get_all(
        "Rental Contract",
        filters={"school_account": customer, "status": ["in", ["Active", "Overdue"]]},
        fields=["name", "instrument", "serial_no", "status", "due_date"],
        order_by="due_date asc",
    )


def _fetch_quotes(customer: str) -> list[dict]:
    return frappe.get_all(
        "Repair Estimate",
        filters={"customer": customer, "workflow_state": ["in", ["Sent", "Awaiting Approval"]]},
        fields=["name", "repair_order", "deposit_amount", "sent_on", "approval_link"],
        order_by="sent_on desc",
    )


def _fetch_repairs(customer: str) -> list[dict]:
    return frappe.get_all(
        "Repair Order",
        filters={"customer": customer, "workflow_state": ["in", ["Ready to Ship", "QC"]]},
        fields=["name", "instrument", "workflow_state", "sla_due"],
        order_by="sla_due asc",
    )

