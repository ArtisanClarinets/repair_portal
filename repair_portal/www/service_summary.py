"""Summary of repair logs accessible to the user."""

import frappe


def get_context(context):
    """Return context for the service summary list."""
    frappe.only_for("Technician")

    user = frappe.session.user
    roles = frappe.get_roles(user)

    if "Technician" in roles or "System Manager" in roles:
        filters = {}
    else:
        client = frappe.db.get_value("Client Profile", {"linked_user": user}, "name")
        filters = {"client_profile": client} if client else {"owner": user}

    context.title = "Service Summary"
    context.repair_logs = frappe.get_all(
        "Repair Log",
        filters=filters,
        fields=["instrument", "date", "technician", "description"],
        order_by="date desc",
    )
    if not context.repair_logs:
        context.empty_message = "No service logs found for your profile."
    return context