# Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/intake/api.py
# Last Updated: 2025-09-19
# Version: v1.0.0 (Dedicated API surface; least-privilege fields; strict permissions)
# Purpose:
#   Whitelisted server endpoints for the Intake module.
#   • Move UI fetchers out of DocType controllers
#   • Guard every endpoint with allow_guest=False and explicit permission checks
#   • Return only the fields the client UI needs (principle of least privilege)
#
# Endpoints:
#   - get_instrument_by_serial(serial_no: str) -> dict | None
#   - get_instrument_inspection_name(intake_record_id: str) -> str | None
#
# Notes:
#   • This file intentionally duplicates a minimal helper to detect Instrument.serial_no field type.
#   • Update client calls to:
#       repair_portal.intake.api.get_instrument_by_serial
#       repair_portal.intake.api.get_instrument_inspection_name

from __future__ import annotations

from typing import Any

import frappe
from frappe import _

# Serial utility (single source of truth for serial normalization / lookup)
from repair_portal.utils.serials import find_by_serial

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_ALLOWED_INSTRUMENT_FIELDS = [
	"name",
	"brand",  # will be renamed to "manufacturer" for the client
	"model",
	"clarinet_type",
	"body_material",
	"key_plating",
	"year_of_manufacture",
	"instrument_category",
]


def _get_instrument_serial_field_type() -> str | None:
	"""
	Return the fieldtype of Instrument.serial_no ('Link' | 'Data' | None).
	Kept dynamic to support both legacy and modern schemas.
	"""
	try:
		meta = frappe.get_meta("Instrument")
		df = meta.get_field("serial_no")
		return getattr(df, "fieldtype", None) if df else None
	except Exception:
		return None


def _massage_instrument_fields(data: dict[str, Any]) -> dict[str, Any]:
	"""
	Apply least-privilege filtering and rename keys for the client.
	- Keep only _ALLOWED_INSTRUMENT_FIELDS.
	- Rename 'brand' -> 'manufacturer' to match intake UI expectations.
	"""
	out: dict[str, Any] = {k: data.get(k) for k in _ALLOWED_INSTRUMENT_FIELDS if k in data}
	if "brand" in out:
		out["manufacturer"] = out.pop("brand")
	return out


def _ensure_read_permission() -> None:
	"""
	Guard all endpoints with an explicit permission check.
	We use the Clarinet Intake doctype because these APIs are consumed by the intake UI.
	"""
	if not frappe.has_permission("Clarinet Intake", ptype="read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@frappe.whitelist(allow_guest=False)
def get_instrument_by_serial(serial_no: str) -> dict[str, Any] | None:
	"""
	Secure, backwards-compatible fetch of Instrument details by a user-entered serial.

	Resolution order:
	  1) If Instrument.serial_no is a Link → 'Instrument Serial Number':
	     • Normalize via utils.serials.find_by_serial()
	     • Match Instrument where serial_no == ISN name
	  2) Legacy fallback (Data field):
	     • Match Instrument where serial_no == raw input

	Returns a dict with a minimal field set or None.
	"""
	_ensure_read_permission()

	if not serial_no:
		return None

	# Prefer ISN path when Instrument.serial_no is Link
	field_type = _get_instrument_serial_field_type()
	isn = find_by_serial(serial_no)

	if field_type == "Link" and isn and isn.get("name"):
		instr_name = frappe.db.get_value("Instrument", {"serial_no": isn["name"]}, "name")
		if instr_name:
			data = frappe.db.get_value(
				"Instrument",
				instr_name,
				_ALLOWED_INSTRUMENT_FIELDS,
				as_dict=True,
			)
			return _massage_instrument_fields(data) if data else None

	# Legacy Data fallback
	data = frappe.db.get_value(
		"Instrument",
		{"serial_no": serial_no},
		_ALLOWED_INSTRUMENT_FIELDS,
		as_dict=True,
	)
	return _massage_instrument_fields(data) if data else None


@frappe.whitelist(allow_guest=False)
def get_instrument_inspection_name(intake_record_id: str) -> str | None:
	"""
	Return the Instrument Inspection name linked to a given intake, if any.
	"""
	_ensure_read_permission()

	if not intake_record_id:
		return None

	return frappe.db.get_value(
		"Instrument Inspection", {"intake_record_id": intake_record_id}, "name"
	)
