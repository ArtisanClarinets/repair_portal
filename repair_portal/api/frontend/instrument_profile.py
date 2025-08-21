# Path: repair_portal/api/frontend/instrument_profile.py
# Last Updated: 2025-08-14
# Version: v1.2
# Purpose: Frontend APIs for Instrument and the aggregated Instrument Profile snapshot.
from __future__ import annotations

import frappe
from frappe import _

from repair_portal.instrument_profile.services.profile_sync import (
	get_snapshot as _get_snapshot,
)
from repair_portal.instrument_profile.services.profile_sync import (
	sync_now as _sync_now,
)


@frappe.whitelist(allow_guest=False)
def get(instrument_id=None):
	"""Fetch a single Instrument by ID with basic fields (backward compatible)."""
	if not instrument_id:
		frappe.throw(_("Instrument ID is required"))

	user = frappe.session.user
	roles = set(frappe.get_roles(user))
	staff_roles = {"Technician", "Repair Manager", "System Manager"}
	is_staff = bool(roles & staff_roles)
	fields = [
		"name",
		"serial_no",
		"instrument_type",
		"brand",
		"model",
		"customer",
		"current_status",
	]

	if is_staff:
		return frappe.db.get_value("Instrument", instrument_id, fields, as_dict=True)

	email = frappe.db.get_value("User", user, "email")
	customer = frappe.db.get_value("Customer", {"email_id": email})
	doc = frappe.db.get_value("Instrument", instrument_id, fields, as_dict=True)
	if not customer or not doc or doc.get("customer") != customer:
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	return doc


@frappe.whitelist(allow_guest=False)
def list_for_user():
	"""List Instruments for current user. Staff see all; Customers see their own."""
	user = frappe.session.user
	roles = set(frappe.get_roles(user))
	staff_roles = {"Technician", "Repair Manager", "System Manager"}
	is_staff = bool(roles & staff_roles)

	fields = [
		"name",
		"serial_no",
		"instrument_type",
		"brand",
		"model",
		"customer",
		"current_status",
	]
	docs = frappe.get_all("Instrument", fields=fields)
	if is_staff:
		return docs

	email = frappe.db.get_value("User", user, "email")
	customer = frappe.db.get_value("Customer", {"email_id": email})
	return [d for d in docs if (customer and d.customer and d.customer == customer)]


@frappe.whitelist(allow_guest=False)
def get_profile(instrument=None, profile=None):
	"""
	Return the fully-synced Instrument Profile document (scalar snapshot only).
	For an aggregated "everything" snapshot, call get_profile_snapshot.
	"""
	if not instrument and not profile:
		frappe.throw(_("Provide instrument or profile"))
	if not profile and instrument:
		res = _sync_now(instrument=instrument)
		profile = res.get("profile")
	else:
		_sync_now(profile=profile)

	return frappe.get_doc("Instrument Profile", profile).as_dict()


@frappe.whitelist(allow_guest=False)
def get_profile_snapshot(instrument=None, profile=None):
	"""
	Return the aggregated snapshot for UI: instrument + owner + serial record +
	accessories, media, condition history, interactions (if doctypes exist).
	"""
	if not instrument and not profile:
		frappe.throw(_("Provide instrument or profile"))
	return _get_snapshot(instrument=instrument, profile=profile)
