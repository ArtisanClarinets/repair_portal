import frappe

def get_context(context):
    user = frappe.session.user
    repairs = frappe.get_all(
        "Repair Log",
        filters={"owner": user},
        fields=["name", "instrument", "date", "status", "description"]
    )
    context.repairs = repairs
    context.empty_message = "No repairs found for your account."
    return context
