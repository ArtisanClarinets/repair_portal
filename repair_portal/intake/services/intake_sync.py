# intake/services/intake_sync.py
import frappe


def upsert_customer(data: dict) -> str:
	"""Returns Customer name."""
	cust_name = data["customer_name"].strip()

	customer = frappe.get_doc(
		{"doctype": "Customer", "customer_name": cust_name, "customer_type": "Individual"}
	)
	customer.update({"customer_group": "All Customer Groups"})  # or your default
	customer.insert(ignore_permissions=True, ignore_if_duplicate=True)

	# Contact
	contact = frappe.get_all("Contact", filters={"email_id": data["email"]}, pluck="name")
	if contact:
		contact = frappe.get_doc("Contact", contact[0])
	else:
		contact = frappe.get_doc(
			{
				"doctype": "Contact",
				"first_name": cust_name.split()[0],
				"last_name": " ".join(cust_name.split()[1:]),
				"email_ids": [{"email_id": data["email"], "is_primary": 1}],
				"phone_nos": [{"phone": data["phone"], "is_primary_phone": 1}],
				"links": [{"link_doctype": "Customer", "link_name": customer.name}],
			}
		)
		contact.insert(ignore_permissions=True)

	# Address
	_upsert_address(customer.name, data) # type: ignore

	return customer.name # type: ignore
