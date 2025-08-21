# File Header Template
# Relative Path: repair_portal/api/frontend/customer_profile.py
# Last Updated: 2025-07-27
# Version: v1.0
# Purpose: Customer profile view and edit endpoints for frontend use
# Dependencies: frappe, api_security, error_handler, database_optimizer

import frappe

from repair_portal.utils import api_security, database_optimizer, error_handler


@frappe.whitelist(allow_guest=False)
def get_customer_profile():
	"""
	Returns current logged-in user's basic profile info.

	Returns:
	    dict: { "full_name": ..., "email": ..., "phone": ..., "address": ... }
	"""
	try:
		user = api_security.get_logged_in_user()
		profile = frappe.get_doc("User", user)
		return {
			"full_name": profile.full_name or profile.first_name or user,
			"email": profile.email or profile.name,
			"phone": getattr(profile, "phone", "") or "",
			"address": getattr(profile, "address", "") or "",
		}
	except Exception as e:
		error_handler.log_and_raise(e, "Failed to fetch customer profile.")


@frappe.whitelist(allow_guest=False)
def update_customer_profile(full_name, email, phone=None, address=None):
	"""
	Updates current user's basic profile info.

	Args:
	    full_name (str): New full name
	    email (str): New email
	    phone (str, optional): New phone
	    address (str, optional): New address

	Returns:
	    dict: Confirmation
	"""
	try:
		user = api_security.get_logged_in_user()
		profile = frappe.get_doc("User", user)
		# Basic field updates
		profile.full_name = full_name
		profile.email = email
		if phone is not None:
			profile.phone = phone
		if address is not None:
			profile.address = address
		profile.save(ignore_permissions=True)
		database_optimizer.touch_user(user)  # stub, does nothing for now
		return {"status": "success"}
	except Exception as e:
		error_handler.log_and_raise(e, "Failed to update customer profile.")
