import frappe

def get_context(context):
    user = frappe.session.user
    client = frappe.db.get_value("Client Profile", {"linked_user": user}, "name")

    filters = {"client_profile": client} if client else {"owner": user}

    context.title = "My Instruments"
    context.introduction = "All clarinets linked to your profile."
    context.instruments = frappe.get_all("Instrument Profile", filters=filters, fields=[
        "name", "serial_number", "brand", "model", "instrument_type", "status", "route"
    ])