# repair_portal/customer/workflow_action_master/workflow_action_master.py
#
# Version: 2.0.1
#
# Purpose: Master controller for all Customer workflow transitions.
# This script is designed to be the single source of truth for what should
# happen when a Customer document transitions from one state to another.
#
# ---------------------------------------------------------------------------
from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import get_url

# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------


def handle_workflow_action(doc: Document, action: str):
	"""
	This function is called from the Customer DocType's `after_workflow_action` hook.
	It routes the action to the appropriate handler.
	"""
	if action == "Activate":
		handle_activation(doc)
	elif action == "Approve":
		handle_approval(doc)
	elif action == "Archive":
		archive_children(doc)
	elif action == "Restore":
		restore_children(doc)
	elif action == "Delete":
		handle_delete(doc)


# ---------------------------------------------------------------------------
# Workflow Action Handlers
# ---------------------------------------------------------------------------


def handle_activation(doc: Document):
	"""
	Handles the 'Activate' action.
	- Validates customer data.
	- Creates a Player Profile if one doesn't exist.
	- Sends a welcome email.
	"""
	_validate_activation_requirements(doc)

	if not frappe.db.exists("Player Profile", {"customer": doc.name}):
		frappe.get_doc(
			{
				"doctype": "Player Profile",
				"customer": doc.name,
				"player_name": frappe.db.get_value("Customer", doc.customer, "customer_name"),
			}
		).insert(ignore_permissions=True)
		doc.add_comment("Workflow", "Auto-created first Player Profile.")

	email = frappe.db.get_value("Customer", doc.customer, "email_id")
	if email:
		try:
			frappe.enqueue(
				"frappe.core.doctype.communication.email.sendmail",
				queue="short",
				recipients=[email],
				subject="Your Artisan Clarinets portal is live",
				message=(
					"Welcome! Manage your repairs online at "
					f"<a href='{get_url('/login')}'>{get_url('/login')}</a>"
				),
			)
			doc.add_comment("Workflow", "Sent welcome email to client.")
		except Exception:
			frappe.log_error(frappe.get_traceback(), "Customer: welcome-email failure")


def handle_approval(doc: Document):
	"""
	Handles the 'Approve' action.
	"""
	doc.add_comment("Workflow", "Profile has been approved.")
	frappe.msgprint("Customer approved.")


def archive_children(doc: Document):
	"""
	Handles the 'Archive' action.
	- Archives all child Player and Instrument Profiles.
	"""
	players = frappe.get_all("Player Profile", {"customer": doc.name})
	for p in players:
		pp = frappe.get_doc("Player Profile", p.name)
		_set_state(pp, "Archived")

		instruments = frappe.get_all("Instrument Profile", {"player_profile": pp.name})
		for i in instruments:
			ip = frappe.get_doc("Instrument Profile", i.name)
			_set_state(ip, "Archived")

	doc.add_comment("Workflow", "All child Player and Instrument Profiles have been archived.")


def restore_children(doc: Document):
	"""
	Handles the 'Restore' action.
	- Restores all child Player and Instrument Profiles to 'Active'.
	"""
	players = frappe.get_all("Player Profile", {"customer": doc.name})
	for p in players:
		pp = frappe.get_doc("Player Profile", p.name)
		_set_state(pp, "Active")  # Restoring to Active state

		instruments = frappe.get_all("Instrument Profile", {"player_profile": pp.name})
		for i in instruments:
			ip = frappe.get_doc("Instrument Profile", i.name)
			_set_state(ip, "Active")  # Restoring to Active state

	doc.add_comment("Workflow", "All child Player and Instrument Profiles have been restored to Active.")


def handle_delete(doc: Document):
	"""
	Handles the 'Delete' action.
	"""
	doc.add_comment("Workflow", "Profile has been marked for deletion.")


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------


def _validate_activation_requirements(doc: Document):
	"""
	Ensures that the customer has a name and email before activation.
	"""
	cust = frappe.get_doc("Customer", doc.customer)
	missing = [
		label
		for field, label in [("customer_name", "Customer Name"), ("email_id", "Email")]
		if not cust.get(field)
	]
	if missing:
		frappe.throw(
			"Cannot activate; fix Customer master:<br><ul>"
			+ "".join(f"<li>{m}</li>" for m in missing)
			+ "</ul>"
		)


def _set_state(doc: Document, state: str):
	"""
	Helper to set a workflow state field consistently on a document.
	"""
	state_field = "profile_status" if hasattr(doc, "profile_status") else "workflow_state"
	if hasattr(doc, state_field):
		setattr(doc, state_field, state)
		doc.save(ignore_permissions=True)  # removed frappe.db.commit() here
