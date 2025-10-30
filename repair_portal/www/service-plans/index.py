"""Portal view for service plan enrollments."""
from __future__ import annotations

from typing import List

import frappe
from frappe import _

from repair_portal.repair_portal.utils.feature_flags import is_enabled


no_cache = 1


def get_context(context: dict) -> dict:
    if not is_enabled("enable_service_plans"):
        frappe.throw(_("Service plan portal is disabled."), frappe.PermissionError)

    enrollments = []
    token = frappe.form_dict.get("token")
    if token:
        enrollments = _fetch_by_token(token)
    elif frappe.session.user != "Guest":
        enrollments = _fetch_for_user(frappe.session.user)
    context["enrollments"] = enrollments
    context["page_title"] = _("Service Plans")
    return context


def _fetch_by_token(token: str) -> List[dict]:
    docs = frappe.get_all(
        "Service Plan Enrollment",
        filters={"portal_token": token},
        fields=[
            "name",
            "service_plan",
            "status",
            "next_billing_date",
            "last_billed_on",
            "auto_pay_enabled",
        ],
    )
    if not docs:
        frappe.throw(_("No service plans found for token."), frappe.PermissionError)
    return docs


def _fetch_for_user(user: str) -> List[dict]:
    customer = _resolve_customer_from_user(user)
    if not customer:
        return []
    return frappe.get_all(
        "Service Plan Enrollment",
        filters={"customer": customer},
        fields=[
            "name",
            "service_plan",
            "status",
            "next_billing_date",
            "last_billed_on",
            "auto_pay_enabled",
        ],
        order_by="next_billing_date asc",
    )


def _resolve_customer_from_user(user: str) -> str | None:
    contact = frappe.db.get_value("Contact", {"user": user}, "name")
    if not contact:
        return None
    link = frappe.db.get_value(
        "Dynamic Link",
        {
            "parenttype": "Contact",
            "parent": contact,
            "link_doctype": "Customer",
        },
        "link_name",
    )
    return link

