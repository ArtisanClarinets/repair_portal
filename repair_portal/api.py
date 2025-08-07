# repair_portal/api.py
# Last Updated: 2025-07-25
# Version: v1.4.2
# Public API for repair-portal Vue frontend

import frappe
from frappe.utils import now

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _assert_own_or_permitted(doc, perm_type: str):
    """Raise if current user has no right to doc for given perm_type."""
    if doc.owner != frappe.session.user and not frappe.has_permission(doc.doctype, perm_type, doc=doc):
        frappe.throw("You are not authorized to perform this action.")

# ----------------------------------------------------------------------
# Read
# ----------------------------------------------------------------------

@frappe.whitelist()
def get_customer(customer_id: str) -> dict:
    """
    Fetch a Customer profile plus dashboard counters.

    :param customer_id: Customer.name
    :return: {"status": "success", "data": {...}} or {"error": "..."}
    """
    try:
        if not customer_id:
            frappe.throw("Missing customer_id")

        doc = frappe.get_doc("Customer", customer_id, ignore_permissions=True)  # type: ignore # updated line
        _assert_own_or_permitted(doc, "read")

        result = {
            "name": doc.name,
            "full_name": doc.full_name,
            "email": doc.email_id,
            "phone": doc.phone,
            "address": doc.address,
            "total_players": frappe.db.count("Player Profile", {"customer": doc.name}),
            "total_instruments": frappe.db.count("Instrument Profile", {"customer": doc.name}),
            "total_services": frappe.db.count("Service", {"customer": doc.name}),
        }

        repairs_by_status = frappe.db.get_all(
            "Repair",
            filters={"customer": doc.name},
            fields=["status", "count(name) as total"],
            group_by="status",
            as_list=False,
        )
        for row in repairs_by_status:
            result[f"total_repairs_{row.status.lower()}"] = row.total

        result["total_repairs"] = sum(r.total for r in repairs_by_status)

        return {"status": "success", "data": result}

    except Exception as e:
        msg = f"Error fetching customer profile '{customer_id}': {e}"
        frappe.log_error(frappe.get_traceback(), msg)
        return {"error": msg}

# ----------------------------------------------------------------------
# Update
# ----------------------------------------------------------------------

@frappe.whitelist()
def update_customer(customer: dict | str) -> dict:
    """
    Update a Customer profile.

    :param customer: dict with at least 'name'
    :return: {"status": "success"} or {"error": "..."}
    """
    try:
        if isinstance(customer, str):
            customer = frappe.parse_json(customer) or {}

        if not (customer and customer.get("name")):
            frappe.throw("Missing customer data or name field")

        cust = frappe._dict(customer) # type: ignore

        doc = frappe.get_doc("Customer", cust.name, ignore_permissions=True)
        _assert_own_or_permitted(doc, "write")

        doc.update(
            {
                "full_name": cust.get("full_name"),
                "email_id": cust.get("email"),
                "phone": cust.get("phone"),
                "address": cust.get("address"),
                "modified_by_portal": now(),
            }
        )
        doc.save()

        return {"status": "success"}

    except Exception as e:
        msg = f"Error updating customer '{cust.get('name', '?')}': {e}"
        frappe.log_error(frappe.get_traceback(), msg)
        return {"error": msg}