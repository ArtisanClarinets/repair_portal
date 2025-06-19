import frappe
from frappe import _

login_required = True


def get_context(context):
    frappe.only_for(("Client", "Technician"))
    name = frappe.form_dict.get("name")
    if not name:
        frappe.throw(_("Repair Request not specified"))

    doc = frappe.get_doc("Repair Request", name)
    user = frappe.session.user
    if "Technician" not in frappe.get_roles(user) and doc.customer != user:
        frappe.throw(_("Not permitted"))

    updates = frappe.get_all(
        "Pulse Update",
        fields=["name", "update_time", "status", "details", "percent_complete"],
        filters={"repair_request": name},
        order_by="update_time asc",
    )

    context.repair_request = doc
    context.updates = updates
    context.updates_json = frappe.safe_json.dumps(updates)
    context.channel = f"repair_pulse_{name}"
    return context
