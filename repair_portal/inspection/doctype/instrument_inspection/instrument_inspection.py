# File Header Template
# Relative Path: repair_portal/inspection/doctype/instrument_inspection/instrument_inspection.py
# Last Updated: 2025-08-14
# Version: v2.0.0 (First-class ISN; graceful legacy handling)
# Purpose: Controller for Instrument Inspection DocType - validation, automation, and audit for inspections
#          (inventory, repair, maintenance, QA). Ensures serial_no links to Instrument Serial Number (ISN),
#          auto-resolves/creates ISN from raw/legacy values, and syncs key specs to Instrument Profile.
# Dependencies: frappe, Inspection Finding, Tenon Measurement, Tone Hole Inspection Record, Instrument Profile
#               repair_portal.utils.serials (ensure_instrument_serial, find_by_serial)

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document

# ---- ISN utilities (single source of truth) ----
# Support either app path to avoid import-order issues.
try:
	from repair_portal.utils.serials import (  # preferred 
		ensure_instrument_serial,
	)
	from repair_portal.utils.serials import (
		find_by_serial as isn_find_by_serial, 
	)
except Exception:
	from repair_portal.utils.serials import (  # fallback
		ensure_instrument_serial,
	)
	from repair_portal.utils.serials import (
		find_by_serial as isn_find_by_serial,
	)


class InstrumentInspection(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from repair_portal.instrument_profile.doctype.instrument_accessory.instrument_accessory import (
			InstrumentAccessory,
		)
		from repair_portal.instrument_profile.doctype.instrument_photo.instrument_photo import (
			InstrumentPhoto,
		)
		from repair_portal.repair_logging.doctype.tenon_measurement.tenon_measurement import (
			TenonMeasurement,
		)
		from repair_portal.repair_logging.doctype.tone_hole_inspection_record.tone_hole_inspection_record import (
			ToneHoleInspectionRecord,
		)
		from repair_portal.repair_logging.doctype.visual_inspection.visual_inspection import (
			VisualInspection,
		)

		accessory_log: DF.Table[InstrumentAccessory]
		acclimatization_controlled_env: DF.Check
		acclimatization_playing_schedule: DF.Check
		acclimatization_swabbing: DF.Check
		amended_from: DF.Link | None
		audio_video_demos: DF.Literal["Instrument Media"]
		body_material: DF.Data | None
		bore_condition: DF.Literal["Clean", "Debris Present", "Irregularities Visible"]
		bore_measurement: DF.Float
		bore_notes: DF.SmallText | None
		bore_style: DF.Data | None
		clarinet_intake: DF.Link | None
		condition: DF.Table[VisualInspection]
		current_location: DF.Data | None
		current_status: DF.Literal["For Sale", "In Workshop", "With Customer", "Sold", "Archived"]
		customer: DF.Link | None
		hygrometer_photo: DF.AttachImage | None
		inspected_by: DF.Link
		inspection_date: DF.Date | None
		inspection_type: DF.Literal["New Inventory", "Repair", "Maintenance", "QA", "Other"]
		instrument_delivered: DF.Check
		intake_record_id: DF.Link | None
		key: DF.Literal["B♭", "A", "E♭", "C", "D"]
		key_plating: DF.Data | None
		key_system: DF.Literal["Boehm", "Albert", "Oehler", "Other"]
		manufacturer: DF.Data | None
		marketing_photos: DF.Table[InstrumentPhoto]
		model: DF.Data | None
		notes: DF.Text | None
		number_of_keys_rings: DF.Data | None
		overall_condition: DF.Literal["Excellent", "Good", "Fair", "Poor"]
		pad_type_current: DF.Data | None
		pitch_standard: DF.Data | None
		preliminary_estimate: DF.Currency
		profile_image: DF.AttachImage | None
		qc_certificate: DF.Attach | None
		rested_unopened: DF.Check
		serial_no: DF.Link
		service_photos: DF.Table[InstrumentPhoto]
		spring_type: DF.Data | None
		tenon_fit_assessment: DF.Table[TenonMeasurement]
		thumb_rest: DF.Data | None
		tone_hole_inspection: DF.Table[ToneHoleInspectionRecord]
		tone_hole_notes: DF.Text | None
		tone_hole_style: DF.Data | None
		unboxing_rh: DF.Float
		unboxing_temperature: DF.Float
		unboxing_time: DF.Datetime | None
		wood_type: DF.Literal["Grenadilla", "Mopane", "Cocobolo", "Synthetic", "Other"]
	# end: auto-generated types

	# ----------------------
	# Lifecycle
	# ----------------------
	def before_validate(self):
		"""
		Ensure serial_no is a valid ISN docname:
		  - If user pasted a raw string or an ERPNext 'Serial No' name, resolve/create ISN and assign its docname.
		  - If already an ISN docname, keep as-is.
		This guarantees mandatory + link validation will pass.
		"""
		try:
			self._ensure_isn_on_self()
		except Exception:
			frappe.log_error(title="InstrumentInspection.before_validate", message=frappe.get_traceback())
			# Let validate raise the right error if needed

	def validate(self) -> None:
		"""
		Validation hook to enforce business rules for each inspection type.
		Logs any exceptions for audit. Also supports autofill from Instrument.
		"""
		try:
			# Ensure serial_no uniqueness (now that it's guaranteed to be ISN docname)
			self._validate_unique_serial_smart()

			# Autofill key & wood_type (and helpful fields) from Instrument
			self._autofill_from_instrument()

			# Required fields for New Inventory
			if self.inspection_type == "New Inventory":
				missing = [
					f for f in ["manufacturer", "model", "key", "wood_type"] if not getattr(self, f, None)
				]
				if missing:
					frappe.throw(
						_("Missing required field(s) for New Inventory: {0}").format(", ".join(missing))
					)

			# Customer fields only for non-inventory
			if self.inspection_type == "New Inventory" and (self.customer or self.preliminary_estimate):
				frappe.throw(_("Customer and pricing fields must be empty for New Inventory inspections."))
		except Exception:
			frappe.log_error(title="InstrumentInspection.validate", message=frappe.get_traceback())
			raise

	def on_submit(self) -> None:
		"""
		On submit, upsert Instrument Profile for the resolved instrument.
		"""
		try:
			instrument_name, _ = self._resolve_instrument_by_serial(self.serial_no)
			target_instrument = instrument_name or self.serial_no  # conservative fallback

			data = {
				"body_material": self.body_material,
				"key_plating": self.key_plating,
				"key_system": self.key_system,
				"number_of_keys_rings": self.number_of_keys_rings,
				"pitch_standard": self.pitch_standard,
				"bore_style": self.bore_style,
				"bore_measurement": self.bore_measurement,
				"tone_hole_style": self.tone_hole_style,
				"thumb_rest": self.thumb_rest,
				"spring_type": self.spring_type,
				"pad_type_current": self.pad_type_current,
				"current_status": self.current_status,
				"current_location": self.current_location,
				"profile_image": self.profile_image,
				# TODO: map child tables (photos/media/accessories) as needed
			}

			profile_name = frappe.db.get_value("Instrument Profile", {"instrument": target_instrument})
			if profile_name:
				profile = frappe.get_doc("Instrument Profile", profile_name) # type: ignore
				for k, v in data.items():
					if v not in (None, "", []):
						profile.set(k, v)
				profile.save(ignore_permissions=True)
			else:
				payload = {"doctype": "Instrument Profile", "instrument": target_instrument}
				payload.update({k: v for k, v in data.items() if v not in (None, "", [])})
				profile = frappe.get_doc(payload)
				profile.insert(ignore_permissions=True)
		except Exception:
			frappe.log_error(title="InstrumentInspection.on_submit", message=frappe.get_traceback())
			# don't raise, to avoid blocking downstream flows

	# ----------------------
	# Internal helpers
	# ----------------------
	def _ensure_isn_on_self(self) -> None:
		"""
		Guarantee that self.serial_no is an **Instrument Serial Number** docname.
		Accepts any of:
		  - ISN docname (noop)
		  - ERPNext 'Serial No' docname (legacy) -> convert to ISN using same text
		  - Raw stamped text -> resolve or create ISN
		"""
		val = (self.serial_no or "").strip()
		if not val:
			return  # let "reqd" enforce presence

		# Already an ISN docname?
		if frappe.db.exists("Instrument Serial Number", val):
			return

		# Legacy: ERPNext Serial No by exact name?
		if frappe.db.exists("Serial No", val):
			# Convert to ISN using the same visible token
			isn_name = ensure_instrument_serial(
				serial_input=val,
				instrument=getattr(self, "instrument", None),
				link_on_instrument=False,
			)
			if not isn_name:
				frappe.throw(
					_("Unable to ensure Instrument Serial Number from legacy Serial No '{0}'").format(val)
				)
			self.serial_no = isn_name
			return

		# Treat as raw stamped text
		row = isn_find_by_serial(val)
		if row and row.get("name"):
			self.serial_no = row["name"]
			return

		# Create a fresh ISN
		isn_name = ensure_instrument_serial(
			serial_input=val, instrument=getattr(self, "instrument", None), link_on_instrument=False
		)
		if not isn_name:
			frappe.throw(_("Unable to create Instrument Serial Number from value '{0}'").format(val))
		self.serial_no = isn_name

	def _validate_unique_serial_smart(self) -> None:
		"""
		Enforce uniqueness for Instrument Inspection by **ISN docname**.
		(The migration guarantees serial_no now points to ISN, so a simple check suffices.)
		"""
		if not self.serial_no:
			return

		duplicate = frappe.db.get_value(
			"Instrument Inspection",
			{"name": ["!=", self.name], "serial_no": self.serial_no},
			"name",
		)
		if duplicate:
			frappe.throw(_("An Instrument Inspection already exists for this serial: {0}").format(duplicate))

	def _autofill_from_instrument(self) -> None:
		"""
		Autofill key & wood_type (and a few safe fields) from the linked Instrument.
		"""
		if not self.serial_no:
			return
		instr_name, instr_doc = self._resolve_instrument_by_serial(self.serial_no)
		if not instr_doc:
			return

		# key: store musical key (B♭, A, etc.) from Instrument.clarinet_type if available
		if not self.key and getattr(instr_doc, "clarinet_type", None):
			self.key = instr_doc.clarinet_type # type: ignore

		# wood_type from Instrument.body_material if available
		if not self.wood_type and getattr(instr_doc, "body_material", None):
			self.wood_type = instr_doc.body_material # type: ignore

		# Also backfill manufacturer & model for convenience
		if not self.manufacturer and getattr(instr_doc, "brand", None):
			self.manufacturer = instr_doc.brand # type: ignore
		if not self.model and getattr(instr_doc, "model", None):
			self.model = instr_doc.model # type: ignore

	# -- Resolution core --

	def _resolve_instrument_by_serial(self, serial_link_or_text: str) -> tuple[str | None, Document | None]:
		"""
		Resolve the Instrument by any serial representation (ISN/legacy/raw).
		Prefers ISN→Instrument. Falls back to legacy pathways for safety.
		Returns: (instrument_name, instrument_doc) or (None, None)
		"""
		token = (serial_link_or_text or "").strip()
		if not token:
			return None, None

		# Case 1: treat input as ISN docname
		if frappe.db.exists("Instrument Serial Number", token):
			isn = frappe.get_value("Instrument Serial Number", token, ["instrument"], as_dict=True)
			if isn and isn.get("instrument") and frappe.db.exists("Instrument", isn["instrument"]): # type: ignore
				doc = frappe.get_doc("Instrument", isn["instrument"]) # type: ignore
				return doc.name, doc

		# Case 2: legacy ERPNext Serial No docname (Instrument.serial_no might have stored it historically)
		if frappe.db.exists("Serial No", token):
			instr_name = frappe.db.get_value("Instrument", {"serial_no": token}, "name")
			if instr_name:
				return instr_name, frappe.get_doc("Instrument", instr_name) # type: ignore

		# Case 3: raw→ISN (normalized), then Instrument
		isn_row = isn_find_by_serial(token)
		if isn_row and isn_row.get("instrument") and frappe.db.exists("Instrument", isn_row["instrument"]):
			doc = frappe.get_doc("Instrument", isn_row["instrument"])
			return doc.name, doc

		# Case 3b: raw→Instrument (legacy Data field)
		instr_name = frappe.db.get_value("Instrument", {"serial_no": token}, "name")
		if instr_name:
			return instr_name, frappe.get_doc("Instrument", instr_name) # type: ignore

		# Case 3c: raw→ISN name stored into Instrument.serial_no (when Instrument.serial_no is a Link)
		if isn_row and isn_row.get("name"):
			instr_name = frappe.db.get_value("Instrument", {"serial_no": isn_row["name"]}, "name")
			if instr_name:
				return instr_name, frappe.get_doc("Instrument", instr_name) # type: ignore

		return None, None

	def _equivalent_serial_identifiers(self, serial_link_or_text: str) -> list[str]:
		"""
		(Kept for reference; no longer used by the simplified uniqueness rule above.)
		Produce a set of equivalent identifiers for a given serial to catch duplicates:
		- The input itself
		- The ISN docname (if resolvable from raw)
		- The ERPNext Serial No docname (if resolvable from raw)
		"""
		eq: list[str] = []
		val = (serial_link_or_text or "").strip()
		if not val:
			return eq

		eq.append(val)

		isn_row = isn_find_by_serial(val) if val else None
		if isn_row and isn_row.get("name"):
			eq.append(isn_row["name"])

		if frappe.db.exists("Serial No", val):
			eq.append(val)

		# Deduplicate
		eq = list(dict.fromkeys(eq))
		return eq
