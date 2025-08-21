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
		doc = frappe.get_doc("Customer", client_id)

		if not frappe.has_permission(doc=doc, ptype="read"):
			raise PermissionError(_("You are not permitted to access this Customer."))

		return {
			"name": doc.name,
			"customer_name": doc.customer_name,
			"contact_email": doc.contact_email,
			"contact_phone": doc.contact_phone,
			"default_address": doc.default_address,
			"billing_address": doc.billing_address,
			"shipping_address": doc.shipping_address,
			"created": doc.creation,
			"modified": doc.modified,
		}

	except PermissionError:
		frappe.log_error(frappe.get_traceback(), "PermissionError in get_customer")
		raise
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Error in get_customer")
		return {"error": str(e)}
