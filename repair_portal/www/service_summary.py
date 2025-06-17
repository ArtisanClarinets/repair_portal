import frappe

def get_context(context):
    user = frappe.session.user
    roles = frappe.get_roles(user)

    if "Technician" in roles or "System Manager" in roles:
        filters = {}  # Show all logs
    else:
        client = frappe.db.get_value("Client Profile", {"linked_user": user}, "name")
        filters = {"client_profile": client} if client else {"owner": user}

    context.repair_logs = frappe.get_all("Repair Log", filters=filters, fields=[
        "instrument", "date", "technician", "description"
    ])