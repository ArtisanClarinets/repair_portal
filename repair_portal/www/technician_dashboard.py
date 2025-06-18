import frappe

def get_context(context):
    user = frappe.session.user
    assigned_repairs = frappe.get_all(
        "Repair Log",
        filters={"technician": user, "status": ["in", ["Assigned", "In Progress"]]},
        fields=["name", "instrument", "date", "status", "description"]
    )
    context.repairs = assigned_repairs
    context.empty_message = "No assigned repairs."
    return context
