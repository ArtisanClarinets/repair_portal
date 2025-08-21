# Path: repair_portal/instrument_profile/services/profile_sync.py
# Last Updated: 2025-08-15
# Version: v1.4
# Purpose: Instrument Profile "materialized view" sync + snapshot aggregation (schema-safe).
from __future__ import annotations

from collections.abc import Sequence

import frappe
from frappe import _

# ISN helpers (soft import if utils not present)
try:
	from repair_portal.utils.serials import (
		ensure_serial_document,  # type: ignore
	)
	from repair_portal.utils.serials import (
		find_by_serial as isn_find_by_serial,  # type: ignore
	)
except Exception:  # pragma: no cover
	isn_find_by_serial = None  # type: ignore

	def ensure_serial_document(serial_input: str, instrument: str) -> str | None:  # type: ignore
		return None


# ---------------------------
# Meta/Schema helpers (safe selectors)
# ---------------------------

_STD_FIELDS = {"name", "owner", "creation", "modified", "modified_by", "docstatus", "idx"}


def _doctype_exists(doctype: str) -> bool:
	return bool(frappe.db.exists("DocType", doctype))


def _meta_fields(doctype: str) -> set[str]:
	meta = frappe.get_meta(doctype)
	return {df.fieldname for df in meta.fields} | _STD_FIELDS


def _safe_fields_for(doctype: str, candidates: Sequence[str]) -> list[str]:
	"""Return only the candidate fields that actually exist on the doctype (always include name)."""
	existing = _meta_fields(doctype)
	out = ["name"]
	for f in candidates:
		if f != "name" and f in existing:
			out.append(f)
	# dedupe, preserve order
	seen, uniq = set(), []
	for f in out:
		if f not in seen:
			uniq.append(f)
			seen.add(f)
	return uniq


def _safe_order_by(doctype: str, preferred_fields: Sequence[str], default_direction: str = "desc") -> str:
	"""
	Pick the first available field from preferred_fields; fall back to 'creation desc'.
	Always suffix with ', creation desc' for stable ordering.
	"""
	existing = _meta_fields(doctype)
	for f in preferred_fields:
		if f in existing:
			return f"{f} {default_direction}, creation desc"
	return "creation desc"


def _safe_get_all(
	doctype: str,
	filters: dict | None,
	field_candidates: Sequence[str],
	order_candidates: Sequence[str],
	as_list: bool = False,
) -> list[frappe._dict]:
	"""get_all that tolerates missing fields and missing order-by columns."""
	if not _doctype_exists(doctype):
		return []
	fields = _safe_fields_for(doctype, field_candidates)
	order_by = _safe_order_by(doctype, order_candidates, "desc")
	return frappe.get_all(doctype, filters=filters, fields=fields, order_by=order_by, as_list=as_list)


# ---------------------------
# Instrument fetch (safe)
# ---------------------------


def _selectable_instrument_fields() -> list[str]:
	"""
	Build a safe field list based on the Instrument DocType that exists on THIS site.
	Avoids OperationalError: Unknown column 'x' in 'SELECT'.
	"""
	candidates = [
		"customer",
		"serial_no",
		"instrument_type",
		"brand",
		"model",
		"clarinet_type",
		"current_status",
		"purchase_date",
		"purchase_order",
		"purchase_receipt",
	]
	return _safe_fields_for("Instrument", candidates)


def _ensure_keys(d: frappe._dict, keys: Sequence[str]) -> None:
	"""Guarantee keys exist in dict (set None if absent)."""
	for k in keys:
		d.setdefault(k, None)


def _get_instrument_doc(instrument: str) -> frappe._dict:
	fields = _selectable_instrument_fields()
	d = frappe.db.get_value("Instrument", instrument, fields, as_dict=True)
	if not d:
		frappe.throw(_("Instrument {0} not found").format(instrument))
	# Ensure downstream keys exist even if not selected
	_ensure_keys(
		d,
		[
			"customer",
			"serial_no",
			"instrument_type",
			"brand",
			"model",
			"clarinet_type",
			"current_status",
			"purchase_date",
			"purchase_order",
			"purchase_receipt",
		],
	)
	return d


# ---------------------------
# ISN + owner helpers
# ---------------------------


def _get_isn(instrument: frappe._dict) -> frappe._dict | None:
	serial_raw = (instrument.serial_no or "").strip()
	if not serial_raw:
		return None

	isn_name: str | None = None
	if isn_find_by_serial:
		isn_name = isn_find_by_serial(serial_input=serial_raw, instrument=instrument.name)  # type: ignore

	if not isn_name and ensure_serial_document:
		isn_name = ensure_serial_document(serial_input=serial_raw, instrument=instrument.name)

	if not isn_name:
		return None

	return frappe.db.get_value(
		"Instrument Serial Number",
		isn_name,
		[
			"name",
			"serial",
			"normalized_serial",
			"warranty_start_date",
			"warranty_end_date",
			"status",
			"verification_status",
		],
		as_dict=True,
	)


def _get_owner_details(customer: str | None) -> frappe._dict | None:
	if not customer:
		return None
	return frappe.db.get_value(
		"Customer",
		customer,
		[
			"name",
			"customer_name",
			"customer_group",
			"territory",
			"default_currency",
			"mobile_no",
			"email_id",
		],
		as_dict=True,
	)


# ---------------------------
# Sync to Instrument Profile
# ---------------------------


def _safe_set_scalar(profile_name: str, field: str, value) -> None:
	"""Set scalar field on Instrument Profile if the field exists (no validate/submit)."""
	if frappe.get_meta("Instrument Profile").has_field(field):
		frappe.db.set_value("Instrument Profile", profile_name, field, value, update_modified=False)


def _ensure_profile(instrument: str) -> str:
	existing = frappe.db.get_value("Instrument Profile", {"instrument": instrument}, "name")
	if existing:
		return existing
	doc = frappe.get_doc({"doctype": "Instrument Profile", "instrument": instrument})
	# Insert without permissions so background jobs work
	doc.insert(ignore_permissions=True)
	return doc.name


def _headline(brand: str | None, model: str | None, serial_no: str | None) -> str:
	b = (brand or "").strip()
	m = (model or "").strip()
	s = (serial_no or "").strip()
	headline = " ".join(x for x in [b, m] if x).strip()
	if s:
		headline = f"{headline} • {s}".strip(" •")
	return headline or (s or "").strip()


def sync_profile(profile_name: str) -> dict[str, str]:
	"""
	Idempotent, low-side-effect sync: updates ONLY scalar snapshot fields
	on Instrument Profile to avoid recursion/loops. Collections are provided
	through the API snapshot (not copied into child tables).
	"""
	try:
		frappe.flags.in_profile_sync = True  # controller guard
		profile = frappe.get_doc("Instrument Profile", profile_name)
		instrument = _get_instrument_doc(profile.instrument)
		owner = _get_owner_details(instrument.customer)
		isn = _get_isn(instrument)

		# scalar fields on Profile (must exist on the DocType)
		_safe_set_scalar(profile.name, "serial_no", instrument.serial_no)
		_safe_set_scalar(profile.name, "brand", instrument.brand)
		_safe_set_scalar(profile.name, "model", instrument.model)

		# Prefer instrument_type, fallback to clarinet_type if present
		inst_cat = instrument.instrument_type or instrument.clarinet_type
		_safe_set_scalar(profile.name, "instrument_category", inst_cat)

		_safe_set_scalar(profile.name, "customer", instrument.customer)
		_safe_set_scalar(profile.name, "owner_name", owner.customer_name if owner else None)

		# Optional commercial fields (may not exist on your Instrument)
		_safe_set_scalar(profile.name, "purchase_date", instrument.purchase_date)
		_safe_set_scalar(profile.name, "purchase_order", instrument.purchase_order)
		_safe_set_scalar(profile.name, "purchase_receipt", instrument.purchase_receipt)

		_safe_set_scalar(profile.name, "status", instrument.current_status or "Unknown")

		if isn:
			_safe_set_scalar(profile.name, "warranty_start_date", isn.warranty_start_date)
			_safe_set_scalar(profile.name, "warranty_end_date", isn.warranty_end_date)

		_safe_set_scalar(
			profile.name,
			"headline",
			_headline(instrument.brand, instrument.model, instrument.serial_no),
		)

		return {"profile": profile.name, "instrument": instrument.name}
	finally:
		frappe.flags.in_profile_sync = False


@frappe.whitelist()
def sync_now(profile: str | None = None, instrument: str | None = None) -> dict[str, str]:
	"""Ensure a profile exists and sync scalar snapshot fields."""
	if not profile and not instrument:
		frappe.throw(_("Provide either profile or instrument"))
	if not profile and instrument:
		profile = _ensure_profile(instrument)
	return sync_profile(profile)  # type: ignore[arg-type]


def on_linked_doc_change(doc, method=None):
	"""
	Hook target: called from doc_events to keep Profile up to date when any
	linked record changes (Instrument / Instrument Serial Number / etc.)
	"""
	instrument = None
	if doc.doctype == "Instrument":
		instrument = doc.name
	elif hasattr(doc, "instrument"):
		instrument = getattr(doc, "instrument", None)

	if not instrument:
		return

	try:
		profile = _ensure_profile(instrument)
		# run now to keep UX snappy; these are cheap scalar updates
		frappe.enqueue(
			"repair_portal.instrument_profile.services.profile_sync.sync_profile",
			queue="short",
			profile_name=profile,
			now=True,
		)
	except Exception:
		frappe.log_error(
			frappe.get_traceback(), f"Instrument Profile sync failed for instrument {instrument}"
		)


# ---------------------------
# Snapshot aggregation (API) — schema-safe lists
# ---------------------------


def _collection_by_instrument(
	doctype: str,
	instrument_name: str,
	field_candidates: Sequence[str],
	order_candidates: Sequence[str],
	instrument_link_field: str = "instrument",
) -> list[frappe._dict]:
	"""
	Return collection rows for a given instrument, but ONLY if:
	- the doctype exists
	- the link field (default 'instrument') exists
	- we select only existing columns
	- we order by an existing column (fallback: creation desc)
	"""
	if not _doctype_exists(doctype):
		return []

	# If the link field doesn't exist, we can't reliably filter -> return empty
	if instrument_link_field not in _meta_fields(doctype):
		return []

	filters = {instrument_link_field: instrument_name}
	return _safe_get_all(
		doctype=doctype,
		filters=filters,
		field_candidates=field_candidates,
		order_candidates=order_candidates,
		as_list=False,
	)


def _aggregate_snapshot(instrument_name: str, profile_name: str) -> dict[str, object]:
	"""
	Return a full snapshot for UI/API without copying lists into the Profile doc:
	- instrument (selected fields)
	- owner
	- isn (Instrument Serial Number)
	- accessories / media / condition / interactions (if doctypes exist)
	"""
	instrument = _get_instrument_doc(instrument_name)
	owner = _get_owner_details(instrument.customer)
	isn = _get_isn(instrument)

	accessories = _collection_by_instrument(
		doctype="Instrument Accessory",
		instrument_name=instrument_name,
		field_candidates=[
			"accessory_type",
			"type",
			"description",
			"acquired_on",
			"removed_on",
			"paired_with",
		],
		order_candidates=["acquired_on", "creation"],
		instrument_link_field="instrument",
	)

	media = _collection_by_instrument(
		doctype="Instrument Media",
		instrument_name=instrument_name,
		field_candidates=["type", "image", "file", "description", "taken_on"],
		order_candidates=["taken_on", "creation"],
		instrument_link_field="instrument",
	)

	conditions = _collection_by_instrument(
		doctype="Instrument Condition Record",
		instrument_name=instrument_name,
		field_candidates=[
			"recorded_on",
			"condition_score",
			"notes",
			"technician",
			"workflow_state",
		],
		order_candidates=["recorded_on", "creation"],
		instrument_link_field="instrument",
	)

	interactions = _collection_by_instrument(
		doctype="Instrument Interaction Log",
		instrument_name=instrument_name,
		field_candidates=["log_type", "message", "owner", "creation"],
		order_candidates=["creation"],
		instrument_link_field="instrument",
	)

	return {
		"instrument": instrument,
		"owner": owner,
		"serial_record": isn,
		"accessories": accessories,
		"media": media,
		"conditions": conditions,
		"interactions": interactions,
		"profile_name": profile_name,
		"headline": _headline(instrument.brand, instrument.model, instrument.serial_no),
	}


@frappe.whitelist(allow_guest=False)
def get_snapshot(instrument: str | None = None, profile: str | None = None) -> dict[str, object]:
	"""
	Public API helper: ensure profile exists + synced, then return the full snapshot.
	"""
	if not instrument and not profile:
		frappe.throw(_("Provide instrument or profile"))
	if not profile and instrument:
		profile = _ensure_profile(instrument)
	res = sync_profile(profile)  # sync scalars
	return _aggregate_snapshot(res["instrument"], res["profile"])
