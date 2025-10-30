# relative path: repair/doctype/pulse_update/pulse_update.py
# updated: 2025-06-27
# version: 1.0
# purpose: Controller for Pulse Update entries linked to Repair Orders.

from __future__ import annotations

import frappe
from frappe.model.document import Document

from repair_portal.customer.security import customers_for_user


class PulseUpdate(Document):
    pass


def get_permission_query_conditions(user: str) -> str:
    if "System Manager" in frappe.get_roles(user) or "Repair Manager" in frappe.get_roles(user):
        return ""
    customers = customers_for_user(user)
    if not customers:
        return "1=0"
    customer_list = ", ".join(frappe.db.escape(customer) for customer in customers)
    return (
        "`tabPulse Update`.`repair_request` IN "
        "(SELECT name FROM `tabRepair Request` WHERE customer IN ({customers}))"
    ).format(customers=customer_list)


def has_permission(doc: PulseUpdate, user: str = "") -> bool:
    if not user:
        user = frappe.session.user
    if "System Manager" in frappe.get_roles(user) or "Repair Manager" in frappe.get_roles(user):
        return True
    customers = customers_for_user(user)
    if not customers:
        return False
    repair_request_customer = frappe.db.get_value("Repair Request", doc.repair_request, "customer")
    return bool(repair_request_customer and repair_request_customer in customers)
