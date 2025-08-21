import frappe


def ensure_user_exists(full_name: str, role: str):
	"""
	Ensure a Frappe user with the given full name and role exists.

	Args:
	    full_name (str): Full name to use for user and email prefix.
	    role (str): Role to assign to the user.

	Returns:
	    str: User ID or email.
	"""
	email = full_name.lower().replace(" ", ".") + "@test.com"
	existing = frappe.db.exists("User", email)
	if not existing:
		user = frappe.get_doc(
			{
				"doctype": "User",
				"first_name": full_name.split()[0],
				"last_name": " ".join(full_name.split()[1:]),
				"email": email,
				"roles": [{"role": role}],
			}
		)
		user.insert(ignore_permissions=True)
		frappe.db.commit()
		return email
	return email
