import frappe
from frappe import _
from frappe.exceptions import PermissionError


def get_customer(client_id: str) -> dict:
    """
    Securely retrieves the client profile data for a given client ID.

    Args:
        client_id (str): The name (ID) of the Customer.

    Returns:
        dict: Dictionary of public client profile fields.
    """
    try:
        doc = frappe.get_doc('Customer', client_id)

        if not frappe.has_permission(doc=doc, ptype='read'):
            raise PermissionError(_('You are not permitted to access this Customer.'))

        return {
            'name': doc.name,
            'customer_name': doc.customer_name,  # type: ignore
            'contact_email': doc.contact_email,  # type: ignore
            'contact_phone': doc.contact_phone,  # type: ignore
            'default_address': doc.default_address,  # type: ignore
            'billing_address': doc.billing_address,  # type: ignore
            'shipping_address': doc.shipping_address,  # type: ignore
            'created': doc.creation,  # type: ignore
            'modified': doc.modified,  # type: ignore
        }

    except PermissionError:
        frappe.log_error(frappe.get_traceback(), 'PermissionError in get_customer')
        raise
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Error in get_customer')
        return {'error': str(e)}
