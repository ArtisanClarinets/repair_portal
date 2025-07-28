import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get(instrument_id=None):
    """
    Fetch a single instrument by ID.
    Staff: access any
    Customer/Player: only if linked by 'customer'
    """
    if not instrument_id:
        frappe.throw(_('Instrument ID is required'))
    user = frappe.session.user
    roles = set(frappe.get_roles(user))
    staff_roles = {"Technician", "Repair Manager", "System Manager"}
    is_staff = bool(roles & staff_roles)
    instrument = frappe.get_doc('Instrument', instrument_id)
    # If not staff, check customer link
    if not is_staff:
        email = frappe.db.get_value('User', user, 'email')
        customer = frappe.db.get_value('Customer', {'email_id': email})
        if not (customer and instrument.customer == customer):
            frappe.throw(_('You are not permitted to view this instrument.'), frappe.PermissionError)
    # Only return fields that exist
    return {
        'name': instrument.name,
        'serial_no': instrument.serial_no,
        'instrument_type': instrument.instrument_type,
        'brand': instrument.brand,
        'model': instrument.model,
        'clarinet_type': getattr(instrument, 'clarinet_type', None),
        'body_material': getattr(instrument, 'body_material', None),
        'keywork_plating': getattr(instrument, 'keywork_plating', None),
        'pitch_standard': getattr(instrument, 'pitch_standard', None),
        'year_of_manufacture': getattr(instrument, 'year_of_manufacture', None),
        'key_plating': getattr(instrument, 'key_plating', None),
        'instrument_category': getattr(instrument, 'instrument_category', None),
        'current_status': getattr(instrument, 'current_status', None),
        'notes': getattr(instrument, 'notes', None),
        'attachments': getattr(instrument, 'attachments', None),
        'customer': instrument.customer,
    }

@frappe.whitelist(allow_guest=False)
def list():
    """
    List all instruments user can view:
    Staff: all instruments.
    Customer/Player: only instruments linked by customer.
    """
    user = frappe.session.user
    roles = set(frappe.get_roles(user))
    staff_roles = {"Technician", "Repair Manager", "System Manager"}
    is_staff = bool(roles & staff_roles)
    instruments = []
    if is_staff:
        docs = frappe.get_all('Instrument', fields=[
            'name', 'serial_no', 'instrument_type', 'brand', 'model', 'customer', 'current_status'
        ])
    else:
        email = frappe.db.get_value('User', user, 'email')
        customer = frappe.db.get_value('Customer', {'email_id': email})
        docs = frappe.get_all('Instrument', fields=[
            'name', 'serial_no', 'instrument_type', 'brand', 'model', 'customer', 'current_status'
        ])
        # Filter to only those linked (safe)
        docs = [
            d for d in docs
            if (customer and d.customer and d.customer == customer)
        ]
    for d in docs:
        instruments.append(d)
    return instruments
