# ---
# File Header:
# Absolute Path: /opt/frappe/erp-bench/apps/repair_portal/repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# Last Updated: 2025-08-14
# Version: v9.2.4 (Fix: use keyworded frappe.log_error with short title to avoid length overflow)
# Purpose: Ensures all intake types auto-create Instrument (custom), Item (for New Inventory), Instrument Serial Number (custom),
#          Instrument Inspection, and (for New Inventory) Clarinet Initial Setup.
#          IMPORTANT: This version never creates ERPNext "Serial No". All serial logic is handled by Instrument Serial Number.
# Dependencies: Clarinet Intake Settings, Instrument, Item, Instrument Serial Number, Instrument Inspection, Clarinet Initial Setup, Instrument Category

from __future__ import annotations

import frappe
from frappe import _
from frappe.model import naming
from frappe.model.document import Document
from frappe.utils import nowdate

from repair_portal.intake.doctype.clarinet_intake_settings.clarinet_intake_settings import (
	get_intake_settings,
)

# Serial utilities (single source of truth) – support either module path
try:
	from repair_portal.utils.serials import (
		attach_to_instrument as link_isn_to_instrument,
	)
	from repair_portal.utils.serials import (  # preferred
		ensure_instrument_serial,
		find_by_serial,
	)
except Exception:
	from repair_portal.utils.serials import (
		attach_to_instrument as link_isn_to_instrument,
	)
	from repair_portal.utils.serials import (  # fallback
		ensure_instrument_serial,
		find_by_serial,
	)

MANDATORY_BY_TYPE = {
	"New Inventory": {"item_code", "item_name", "acquisition_cost", "store_asking_price"},
	"Repair": {"customer", "customers_stated_issue"},
	"Maintenance": {"customer", "customers_stated_issue"},
}


class ClarinetIntake(Document):
	def after_insert(self):
		settings = get_intake_settings()
		try:
			# --- 1. ITEM CREATION (ERPNext) --- #
			# (unchanged) Only for New Inventory
			item_name = self.item_name or self.model or "Instrument" # type: ignore
			item_code = self.item_code or self.serial_no # type: ignore
			item = None
			if self.intake_type == "New Inventory": # type: ignore
				if item_code and not frappe.db.exists("Item", {"item_code": item_code}):
					item = frappe.new_doc("Item")
					item.item_code = item_code # type: ignore
					item.item_name = item_name # type: ignore
					item.item_group = settings.get("default_item_group") or "Clarinets" # type: ignore
					item.stock_uom = settings.get("stock_uom") or "Nos" # type: ignore
					item.description = ( # type: ignore
						f"{self.model or ''} {self.body_material or ''} {self.key_plating or ''}".strip() # type: ignore
					)
					item.is_stock_item = 1 # type: ignore
					item.disabled = 0 # type: ignore
					item.save(ignore_permissions=True)
				else:
					item = frappe.get_doc("Item", item_code) if item_code else None

			# --- 2. INSTRUMENT SERIAL NUMBER (Custom Doctype) --- #
			# REPLACEMENT for ERPNext "Serial No" logic. We NEVER create ERPNext Serial Nos here.
			isn_name: str | None = None
			serial_no_input = (self.serial_no or "").strip() # type: ignore

			if serial_no_input:
				# Try to find an existing ISN (normalized)
				existing_isn = find_by_serial(serial_no_input)  # returns dict or None
				if existing_isn:
					isn_name = existing_isn.get("name")

				if not isn_name:
					# Idempotent creation; do not link yet (Instrument may be created below)
					isn_name = ensure_instrument_serial(
						serial_input=serial_no_input,
						instrument=None,
						link_on_instrument=False,
						status="Active",
					)

			# --- 3. INSTRUMENT CREATION (Custom Doctype) --- #
			# Keep legacy search semantics but prefer ISN if Instrument.serial_no is a Link.
			instrument = None
			if serial_no_input:
				instrument = self._find_existing_instrument_by_serial(serial_no_input, isn_name)

				if not instrument:
					# Create new Instrument
					instrument = frappe.new_doc("Instrument")
					# Attach serial according to field type (Link vs Data)
					serial_field_type = _get_instrument_serial_field_type()

					if serial_field_type == "Link" and isn_name:
						instrument.serial_no = isn_name # type: ignore
					else:
						# Fallback for legacy Data field or when ISN missing
						instrument.serial_no = serial_no_input # type: ignore

					instrument.instrument_type = self.clarinet_type or "B♭ Clarinet" # type: ignore
					instrument.brand = self.manufacturer # type: ignore
					instrument.model = self.model # type: ignore
					instrument.body_material = self.body_material # type: ignore
					instrument.keywork_plating = self.key_plating # type: ignore
					instrument.pitch_standard = self.pitch_standard # type: ignore
					instrument.customer = self.customer if self.intake_type != "New Inventory" else None # type: ignore
					instrument.current_status = "Active" # type: ignore

					# Instrument Category handling (unchanged)
					if self.instrument_category and frappe.db.exists(
						"Instrument Category", self.instrument_category
					):
						instrument.instrument_category = self.instrument_category # type: ignore
					else:
						default_cat = frappe.db.get_value("Instrument Category", {"is_active": 1}, "name")
						if default_cat:
							instrument.instrument_category = default_cat # type: ignore

					instrument.insert(ignore_permissions=True)

				# Set intake link
				self.instrument = instrument.name

				# Link ISN ⇄ Instrument and (if Link field exists) ensure Instrument.serial_no points to ISN
				if isn_name:
					try:
						link_isn_to_instrument(
							isn_name=isn_name, instrument=instrument.name, link_on_instrument=True # type: ignore
						)
					except Exception:
						frappe.log_error(
							title="ClarinetIntake.after_insert",
							message=frappe.get_traceback(),
						)

			# --- 4. Instrument Inspection (all types) --- #
			if not frappe.db.exists("Instrument Inspection", {"intake_record_id": self.name}):
				inspection = frappe.new_doc("Instrument Inspection")
				inspection.intake_record_id = self.name # type: ignore
				inspection.customer = self.customer # type: ignore

				# Compute correct value for serial_no based on the field's target
				insp_serial_value, insp_requires_bypass = self._compute_inspection_serial_value(
					serial_no_input, isn_name
				)
				inspection.serial_no = insp_serial_value # type: ignore

				inspection.instrument = self.instrument # type: ignore
				inspection.brand = self.manufacturer # type: ignore
				inspection.manufacturer = self.manufacturer # type: ignore
				inspection.model = self.model # type: ignore
				inspection.clarinet_type = self.clarinet_type # type: ignore
				inspection.body_material = self.body_material # type: ignore
				inspection.key_plating = self.key_plating # type: ignore
				inspection.inspection_date = self.intake_date or nowdate() # type: ignore
				inspection.status = "Pending" # type: ignore

				# Robust inspected_by fallback (unchanged)
				inspected_by_meta = frappe.get_meta("Instrument Inspection").get_field("inspected_by")
				inspected_by_options = (inspected_by_meta.options or "User") if inspected_by_meta else "User"
				inspected_by_value = None
				if self.employee and frappe.db.exists(inspected_by_options, self.employee): # type: ignore
					inspected_by_value = self.employee # type: ignore
				if not inspected_by_value and frappe.session.user:
					if inspected_by_options == "Employee":
						emp = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
						if emp:
							inspected_by_value = emp
					elif frappe.db.exists(inspected_by_options, frappe.session.user):
						inspected_by_value = frappe.session.user
				if (
					not inspected_by_value
					and getattr(self, "inspected_by", None)
					and frappe.db.exists(inspected_by_options, getattr(self, "inspected_by", None))
				):
					inspected_by_value = getattr(self, "inspected_by", None)
				if not inspected_by_value:
					frappe.throw(
						_(
							f"Cannot create Instrument Inspection: No valid Employee/User found for 'inspected_by'. "
							f"Tried employee: {self.employee or ''}, session_user: {frappe.session.user}, inspected_by: {getattr(self, 'inspected_by', None)}. " # type: ignore
							f"Please ensure at least one exists as a {inspected_by_options} record."
						)
					)
				inspection.inspected_by = inspected_by_value # type: ignore
				allowed_inspection_types = ["New Inventory", "Repair", "Maintenance", "QA", "Other"] # type: ignore
				inspection.inspection_type = ( # type: ignore
					self.intake_type if self.intake_type in allowed_inspection_types else "Other" # type: ignore
				)

				# Insert; if schema is legacy (Link→Serial No) and no ERP serial exists, bypass mandatory (documented)
				if insp_requires_bypass:
					inspection.insert(ignore_permissions=True, ignore_mandatory=True)
					frappe.msgprint(
						_(
							"Instrument Inspection created without a Serial No link because the field is configured "
							"as Link → 'Serial No' and no ERPNext Serial No exists. Please migrate the field to "
							"Link → 'Instrument Serial Number' for full compatibility."
						),
						alert=True,
						indicator="orange",
					)
					frappe.log_error(
						title="ClarinetIntake.after_insert (legacy serial_no field)",
						message=(
							"Instrument Inspection.serial_no is Link→'Serial No' but no ERP Serial exists; "
							"inserted with ignore_mandatory=True. Consider changing field to "
							"Link→'Instrument Serial Number'."
						),
					)
				else:
					inspection.insert(ignore_permissions=True)

				frappe.msgprint(_(f"Instrument Inspection <b>{inspection.name}</b> created."))

			# --- 5. Clarinet Initial Setup (new inventory only) --- #
			if (
				self.intake_type == "New Inventory" # type: ignore
				and settings.get("auto_create_initial_setup", 1)
				and self.instrument
				and not frappe.db.exists("Clarinet Initial Setup", {"instrument": self.instrument})
			):
				setup = frappe.new_doc("Clarinet Initial Setup")
				setup.instrument = self.instrument # type: ignore
				setup.intake = self.name # type: ignore
				setup.setup_date = self.intake_date or nowdate() # type: ignore
				setup.status = "Open" # type: ignore
				setup.insert(ignore_permissions=True)
				frappe.msgprint(_(f"Clarinet Initial Setup <b>{setup.name}</b> created."))

		except Exception:
			frappe.log_error(title="ClarinetIntake.after_insert", message=frappe.get_traceback())
			frappe.throw(
				_(
					"An error occurred during automated record creation. Please check system logs or contact an administrator."
				)
			)

	def _compute_inspection_serial_value(
		self, serial_no_input: str, isn_name: str | None
	) -> tuple[str | None, bool]:
		"""
		Determine what value to put into Instrument Inspection.serial_no, and whether we must bypass mandatory:
		  - If Link to "Instrument Serial Number": ensure/create ISN and return its docname. (no bypass)
		  - If Link to "Serial No": (legacy) try to find ERPNext Serial No by exact name.
		        • If not found, return (None, True) so caller inserts with ignore_mandatory=True.
		  - If Data: return raw serial (no bypass).
		Returns: (value_to_set, requires_mandatory_bypass)
		"""
		df = _get_field_df("Instrument Inspection", "serial_no")
		fieldtype = getattr(df, "fieldtype", None) if df else None
		options = getattr(df, "options", None) if df else None

		# Link → Instrument Serial Number (preferred)
		if fieldtype == "Link" and options == "Instrument Serial Number":
			# If no ISN name yet, ensure it now so link validation never fails
			if not isn_name and serial_no_input:
				isn_name = ensure_instrument_serial(
					serial_input=serial_no_input,
					instrument=None,
					link_on_instrument=False,
					status="Active",
				)
			return isn_name, False

		# Link → Serial No (legacy). We do NOT create ERPNext Serial Nos anymore.
		if fieldtype == "Link" and options == "Serial No":
			if serial_no_input and frappe.db.exists("Serial No", serial_no_input):
				return serial_no_input, False
			# Mandatory will fail; signal caller to bypass
			return None, True

		# Data: just store raw
		return (serial_no_input or None), False

	def _find_existing_instrument_by_serial(self, serial_no_input: str, isn_name: str | None):
		"""
		Backward/forward compatible search:
		  - If Instrument.serial_no is a Link to Instrument Serial Number, search by ISN name.
		  - Else (legacy Data field), search by raw serial string.
		Returns an Instrument doc or None.
		"""
		field_type = _get_instrument_serial_field_type()

		if field_type == "Link" and isn_name:
			name = frappe.db.get_value("Instrument", {"serial_no": isn_name}, "name")
			return frappe.get_doc("Instrument", name) if name else None # type: ignore

		# Legacy Data field or no ISN yet — search by plain serial
		name = frappe.db.get_value("Instrument", {"serial_no": serial_no_input}, "name")
		return frappe.get_doc("Instrument", name) if name else None # type: ignore

	def autoname(self) -> None:
		if not self.intake_record_id:
			settings = get_intake_settings()
			pattern = settings.get("intake_naming_series") or "INTAKE-.{YYYY}.-.#####"
			self.intake_record_id = naming.make_autoname(pattern, doc=self) # type: ignore
		self.name = self.intake_record_id

	def validate(self) -> None:
		self._enforce_dynamic_mandatory_fields()
		self._sync_info_from_existing_instrument()

	def _enforce_dynamic_mandatory_fields(self) -> None:
		missing = [
			self.meta.get_label(f) for f in MANDATORY_BY_TYPE.get(self.intake_type, set()) if not self.get(f) # type: ignore
		]
		if missing:
			frappe.throw(_(f"Required fields are missing: {', '.join(missing)}"), title=_("Validation Error"))

	def _sync_info_from_existing_instrument(self) -> None:
		"""
		If user typed a serial and we already have an Instrument matching it, sync read-only info
		for convenience. Compatible with both Link and Data serial fields.
		"""
		if self.serial_no and not self.instrument: # type: ignore
			serial_no_input = self.serial_no.strip() # type: ignore
			isn = find_by_serial(serial_no_input)
			instr_doc = None

			if isn and isn.get("name"):
				# Prefer Link search
				field_type = _get_instrument_serial_field_type()
				if field_type == "Link":
					instr_name = frappe.db.get_value("Instrument", {"serial_no": isn["name"]}, "name")
					if instr_name:
						instr_doc = frappe.get_doc("Instrument", instr_name) # type: ignore

			if not instr_doc:
				# Legacy Data fall-back
				instr_name = frappe.db.get_value("Instrument", {"serial_no": serial_no_input}, "name")
				if instr_name:
					instr_doc = frappe.get_doc("Instrument", instr_name) # type: ignore

			if instr_doc:
				self.instrument = instr_doc.name
				if not self.manufacturer:
					self.manufacturer = getattr(instr_doc, "brand", None)
				if not self.model:
					self.model = getattr(instr_doc, "model", None)
				if not self.instrument_category:
					self.instrument_category = getattr(instr_doc, "instrument_category", None)


@frappe.whitelist(allow_guest=False)
def get_instrument_by_serial(serial_no: str) -> dict[str, str | int | None] | None:
	"""
	Backwards-compatible fetch:
	  - If Instrument.serial_no is a Link, normalize/resolve serial → ISN → Instrument.
	  - Else (Data), match Instrument.serial_no by plain string.
	"""
	if not serial_no:
		return None

	# Prefer ISN match for Link-style serial_no
	isn = find_by_serial(serial_no)
	if isn and isn.get("name"):
		field_type = _get_instrument_serial_field_type()
		if field_type == "Link":
			instr_name = frappe.db.get_value("Instrument", {"serial_no": isn["name"]}, "name")
			if instr_name:
				data = frappe.db.get_value(
					"Instrument",
					instr_name,
					[ # type: ignore
						"name", 
						"brand",
						"model",
						"clarinet_type",
						"body_material",
						"key_plating",
						"year_of_manufacture",
						"instrument_category",
					],
					as_dict=True,
				)
				if data:
					data["manufacturer"] = data.pop("brand", None) # type: ignore
				return data # type: ignore

	# Legacy Data fallback
	data = frappe.db.get_value(
		"Instrument",
		{"serial_no": serial_no},
		[ # type: ignore
			"name",
			"brand",
			"model",
			"clarinet_type",
			"body_material",
			"key_plating",
			"year_of_manufacture",
			"instrument_category",
		],
		as_dict=True,
	)
	if data:
		data["manufacturer"] = data.pop("brand", None) # type: ignore
	return data # type: ignore


@frappe.whitelist(allow_guest=False)
def get_instrument_inspection_name(intake_record_id: str) -> str | None:
	if not intake_record_id:
		return None
	return frappe.db.get_value("Instrument Inspection", {"intake_record_id": intake_record_id}, "name") # type: ignore


# -----------------------
# Internals (helpers)
# -----------------------


def _get_instrument_serial_field_type() -> str | None:
	"""
	Return the fieldtype of Instrument.serial_no ('Link' | 'Data' | None).
	We keep this dynamic so the controller works against both legacy and new schemas.
	"""
	try:
		meta = frappe.get_meta("Instrument")
		df = meta.get_field("serial_no")
		return getattr(df, "fieldtype", None) if df else None
	except Exception:
		return None


def _get_field_df(doctype: str, fieldname: str):
	"""Return the DocField for (doctype, fieldname) or None."""
	try:
		return frappe.get_meta(doctype).get_field(fieldname)
	except Exception:
		return None
