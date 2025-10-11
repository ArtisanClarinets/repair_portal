# ---
# File Header:
# Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# Last Updated: 2025-09-19
# Version: v9.3.0 (Hardening: idempotent creation guards, legacy-serial compatibility, stricter API permissions)
# Purpose:
#   Ensures all intake types auto-create:
#     • Instrument (custom)
#     • Instrument Serial Number (custom; replaces ERPNext Serial No usage here)
#     • Instrument Inspection (all intake types)
#     • Item (ERPNext Item; New Inventory only)
#     • Clarinet Initial Setup (New Inventory only)
#   IMPORTANT: This controller never creates ERPNext "Serial No". All serial logic is handled by Instrument Serial Number.
# Dependencies:
#   Clarinet Intake Settings, Instrument, Item, Instrument Serial Number, Instrument Inspection,
#   Clarinet Initial Setup, Instrument Category
# ---

from __future__ import annotations

from typing import Optional

import frappe
from frappe import _
from frappe.model import naming
from frappe.model.document import Document
from frappe.utils import nowdate

from repair_portal.intake.doctype.clarinet_intake.clarinet_intake_timeline import (
	add_timeline_entries,
)
from repair_portal.repair_portal_settings.doctype.clarinet_intake_settings.clarinet_intake_settings import (
	get_intake_settings,
)

# Serial utilities (single source of truth)
try:
	from repair_portal.utils.serials import attach_to_instrument as link_isn_to_instrument
	from repair_portal.utils.serials import ensure_instrument_serial, find_by_serial  # preferred
except Exception:  # pragma: no cover - fallback import path
	from repair_portal.utils.serials import attach_to_instrument as link_isn_to_instrument
	from repair_portal.utils.serials import ensure_instrument_serial, find_by_serial  # fallback

from .clarinet_intake_timeline import add_timeline_entries

# Dynamic mandatory fields by intake type
MANDATORY_BY_TYPE = {
        "New Inventory": {"item_code", "item_name", "acquisition_cost", "store_asking_price"},
        "Repair": {"customer", "customers_stated_issue"},
        "Maintenance": {"customer", "customers_stated_issue"},
}

DEFAULT_PLAYER_LEVEL = "Amateur/Hobbyist"
PLAYER_PROFILE = "Player Profile"


class ClarinetIntake(Document):
	"""
	Clarinet Intake controller.

	Current behavior: heavy automation runs in `after_insert` for backward compatibility
	with existing workflows that expect immediate fan-out on creation.
	All creation steps are idempotent (guarded with existence checks).
	"""
	def on_save(self) -> None:
		add_timeline_entries(self, "on_save")
	# ---------------------------------------------------------------------------
	# Naming
	# ---------------------------------------------------------------------------
	def autoname(self) -> None:
		"""Determine intake_record_id using settings-backed pattern; set self.name."""
		if not self.intake_record_id:
			settings = get_intake_settings()
			# Support both legacy & new setting keys
			pattern = (
				settings.get("intake_naming_series")
				or settings.get("intake_id_pattern")
				or "CI-.{YYYY}.-.#####"
			)
			self.intake_record_id = naming.make_autoname(pattern, doc=self)  # type: ignore
		self.name = self.intake_record_id

	# ---------------------------------------------------------------------------
	# Validation
	# ---------------------------------------------------------------------------
        def validate(self) -> None:
                self._enforce_dynamic_mandatory_fields()
                self._sync_info_from_existing_instrument()
                self._ensure_player_profile_link()

	def _enforce_dynamic_mandatory_fields(self) -> None:
		"""Raise if the fields required by intake_type are not present."""
		missing = [
			self.meta.get_label(f)  # type: ignore
			for f in MANDATORY_BY_TYPE.get(self.intake_type, set())  # type: ignore
			if not self.get(f)  # type: ignore
		]
		if missing:
			frappe.throw(
				_(f"Required fields are missing: {', '.join(missing)}"),
				title=_("Validation Error"),
			)

        def _sync_info_from_existing_instrument(self) -> None:
                """
                If user entered a serial and Instrument already exists, populate convenience fields.
                Works whether Instrument.serial_no is a Link (→ Instrument Serial Number) or Data.
                """
                if self.serial_no and not self.instrument:  # type: ignore
                        serial_no_input = self.serial_no.strip()  # type: ignore
                        isn = find_by_serial(serial_no_input)
                        instr_doc = None

			# Prefer the new Link-to-ISN schema
			if isn and isn.get("name"):
				if _get_instrument_serial_field_type() == "Link":
					instr_name = frappe.db.get_value("Instrument", {"serial_no": isn["name"]}, "name")
					if instr_name:
						instr_doc = frappe.get_doc("Instrument", instr_name)  # type: ignore

			# Fallback for legacy Data schema
			if not instr_doc:
				instr_name = frappe.db.get_value("Instrument", {"serial_no": serial_no_input}, "name")
                                if instr_name:
                                        instr_doc = frappe.get_doc("Instrument", instr_name)  # type: ignore

                        # Populate basic fields from the Instrument, if found
                        if instr_doc:
                                self.instrument = instr_doc.name
                                if not self.manufacturer:
                                        self.manufacturer = getattr(instr_doc, "brand", None)
                                if not self.model:
                                        self.model = getattr(instr_doc, "model", None)
                                if not self.instrument_category:
                                        self.instrument_category = getattr(instr_doc, "instrument_category", None)

        def _ensure_player_profile_link(self) -> None:
                if not self.meta.has_field("player_profile"):
                        return
                if not (self.customer or self.customer_email or self.player_profile):
                        return

                profile_doc = self._resolve_player_profile()
                if not profile_doc:
                        return

                updated = False
                if self.customer and profile_doc.customer != self.customer:
                        profile_doc.customer = self.customer
                        updated = True
                if self.customer_phone and not profile_doc.primary_phone:
                        profile_doc.primary_phone = self.customer_phone
                        updated = True

                if updated:
                        profile_doc.save(ignore_permissions=True)

                self.player_profile = profile_doc.name

        def _resolve_player_profile(self) -> Optional[Document]:
                try:
                        if self.player_profile and frappe.db.exists(PLAYER_PROFILE, self.player_profile):
                                return frappe.get_doc(PLAYER_PROFILE, self.player_profile)

                        email = (self.customer_email or "").strip()
                        profile_name: Optional[str] = None
                        if email:
                                profile_name = frappe.db.get_value(PLAYER_PROFILE, {"primary_email": email}, "name")
                        if not profile_name and self.customer:
                                profile_name = frappe.db.get_value(PLAYER_PROFILE, {"customer": self.customer}, "name")

                        if profile_name:
                                return frappe.get_doc(PLAYER_PROFILE, profile_name)

                        if not email:
                                return None

                        player_name = self.customer_full_name or self._get_customer_name() or email
                        payload = {
                                "doctype": PLAYER_PROFILE,
                                "player_name": player_name,
                                "preferred_name": self.customer_full_name,
                                "primary_email": email,
                                "primary_phone": self.customer_phone,
                                "player_level": DEFAULT_PLAYER_LEVEL,
                                "customer": self.customer,
                                "newsletter_subscription": 0,
                                "targeted_marketing_optin": 0,
                        }
                        doc = frappe.get_doc(payload)
                        doc.insert(ignore_permissions=True)
                        return doc
                except Exception:
                        frappe.log_error(
                                title="ClarinetIntake Player Profile", message=frappe.get_traceback()
                        )
                        return None

        def _get_customer_name(self) -> Optional[str]:
                if not self.customer:
                        return None
                try:
                        return frappe.db.get_value("Customer", self.customer, "customer_name")
                except Exception:
                        frappe.log_error(
                                title="ClarinetIntake Customer Lookup", message=frappe.get_traceback()
                        )
                        return None

        def _apply_player_profile_links(self) -> None:
                if not self.meta.has_field("player_profile") or not self.player_profile:
                        return

                try:
                        profile_name = self.player_profile
                        instrument_profile = getattr(self, "instrument_profile", None)
                        if instrument_profile and frappe.db.has_column("Instrument Profile", "owner_player"):
                                frappe.db.set_value("Instrument Profile", instrument_profile, "owner_player", profile_name)
                                if self.customer:
                                        frappe.db.set_value("Instrument Profile", instrument_profile, "customer", self.customer)
                        elif self.instrument and frappe.db.has_column("Instrument Profile", "owner_player"):
                                linked_profile = frappe.db.get_value(
                                        "Instrument Profile", {"instrument": self.instrument}, "name"
                                )
                                if linked_profile:
                                        frappe.db.set_value("Instrument Profile", linked_profile, "owner_player", profile_name)
                                        if self.customer:
                                                frappe.db.set_value("Instrument Profile", linked_profile, "customer", self.customer)
                except Exception:
                        frappe.log_error(
                                title="ClarinetIntake Player Profile Link", message=frappe.get_traceback()
                        )

	# ---------------------------------------------------------------------------
	# Automation
	# ---------------------------------------------------------------------------
	def after_insert(self) -> None:
		"""
		Create (idempotently):
		  • Item (New Inventory only)
		  • Instrument Serial Number (ISN)
		  • Instrument
		  • Instrument Inspection (all intake types)
		  • Clarinet Initial Setup (New Inventory only)
		"""
		settings = get_intake_settings()
		try:
			# --- 1) Item (ERPNext Item, New Inventory only) -------------------------------------
			item = None
			item_name = self.item_name or self.model or "Instrument"  # type: ignore
			item_code = self.item_code or self.serial_no  # type: ignore

			if self.intake_type == "New Inventory":  # type: ignore
				if item_code and not frappe.db.exists("Item", {"item_code": item_code}):
					item = frappe.new_doc("Item")
					item.item_code = item_code  # type: ignore
					item.item_name = item_name  # type: ignore
					item.item_group = settings.get("default_item_group") or "Clarinets"  # type: ignore
					item.stock_uom = settings.get("stock_uom") or "Nos"  # type: ignore
					item.description = (
						f"{self.model or ''} {self.body_material or ''} {self.key_plating or ''}".strip()  # type: ignore
					)
					item.is_stock_item = 1  # type: ignore
					item.disabled = 0  # type: ignore
					item.save(ignore_permissions=True)
				elif item_code:
					item = frappe.get_doc("Item", item_code)  # type: ignore

			# --- 2) Instrument Serial Number (custom; replaces ERPNext Serial No use here) -------
			isn_name: str | None = None
			serial_no_input = (self.serial_no or "").strip()  # type: ignore

			if serial_no_input:
				# Resolve to existing ISN if present
				existing_isn = find_by_serial(serial_no_input)  # dict or None
				if existing_isn:
					isn_name = existing_isn.get("name")

				# If not found, create an ISN (without linking yet)
				if not isn_name:
					isn_name = ensure_instrument_serial(
						serial_input=serial_no_input,
						instrument=None,
						link_on_instrument=False,
						status="Active",
					)

			# --- 3) Instrument (custom) ---------------------------------------------------------
			instrument = None
			if serial_no_input:
				instrument = self._find_existing_instrument_by_serial(serial_no_input, isn_name)

				if not instrument:
					# Create new Instrument
					instrument = frappe.new_doc("Instrument")
					serial_field_type = _get_instrument_serial_field_type()

					# If Instrument.serial_no is a Link→ISN, store ISN name; else store raw serial
					if serial_field_type == "Link" and isn_name:
						instrument.serial_no = isn_name  # type: ignore
					else:
						instrument.serial_no = serial_no_input  # type: ignore

					instrument.instrument_type = self.clarinet_type or "B♭ Clarinet"  # type: ignore
					instrument.brand = self.manufacturer  # type: ignore
					instrument.model = self.model  # type: ignore
					instrument.body_material = self.body_material  # type: ignore
					instrument.keywork_plating = self.key_plating  # type: ignore
					instrument.pitch_standard = self.pitch_standard  # type: ignore
					instrument.customer = (
						self.customer if self.intake_type != "New Inventory" else None  # type: ignore
					)
					instrument.current_status = "Active"  # type: ignore

					# Instrument Category (best effort)
					if self.instrument_category and frappe.db.exists(
						"Instrument Category", self.instrument_category
					):
						instrument.instrument_category = self.instrument_category  # type: ignore
					else:
						default_cat = frappe.db.get_value("Instrument Category", {"is_active": 1}, "name")
						if default_cat:
							instrument.instrument_category = default_cat  # type: ignore

					instrument.insert(ignore_permissions=True)

				# Link back on the Intake
				self.instrument = instrument.name

				# ISN ↔ Instrument link (and make sure Instrument.serial_no points to ISN when field is Link)
				if isn_name:
					try:
						link_isn_to_instrument(
							isn_name=isn_name,
							instrument=instrument.name,  # type: ignore
							link_on_instrument=True,  # type: ignore
						)
					except Exception:
						frappe.log_error(
							title="ClarinetIntake.after_insert (link ISN)",
							message=frappe.get_traceback(),
						)

			# --- 4) Instrument Inspection (all intake types) ------------------------------------
			if not frappe.db.exists("Instrument Inspection", {"intake_record_id": self.name}):
				inspection = frappe.new_doc("Instrument Inspection")
				inspection.intake_record_id = self.name  # type: ignore
				inspection.customer = self.customer  # type: ignore

				# Compute serial field value based on field target type
				insp_serial_value, insp_requires_bypass = self._compute_inspection_serial_value(
					serial_no_input, isn_name
				)
				inspection.serial_no = insp_serial_value  # type: ignore

				inspection.instrument = self.instrument  # type: ignore
				inspection.brand = self.manufacturer  # type: ignore
				inspection.manufacturer = self.manufacturer  # type: ignore
				inspection.model = self.model  # type: ignore
				inspection.clarinet_type = self.clarinet_type  # type: ignore
				inspection.body_material = self.body_material  # type: ignore
				inspection.key_plating = self.key_plating  # type: ignore
				inspection.inspection_date = self.intake_date or nowdate()  # type: ignore
				inspection.status = "Pending"  # type: ignore

				# Set inspected_by best-effort (User/Employee)
				inspected_by_meta = frappe.get_meta("Instrument Inspection").get_field("inspected_by")
				inspected_by_options = (inspected_by_meta.options or "User") if inspected_by_meta else "User"
				inspected_by_value = None

				if self.employee and frappe.db.exists(inspected_by_options, self.employee):  # type: ignore
					inspected_by_value = self.employee  # type: ignore

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
							"Cannot create Instrument Inspection: No valid Employee/User found for 'inspected_by'. "
							f"Tried employee: {self.employee or ''}, session_user: {frappe.session.user}, "
							f"inspected_by: {getattr(self, 'inspected_by', None)}. "
							f"Please ensure at least one exists as a {inspected_by_options} record."
						)
					)
				inspection.inspected_by = inspected_by_value  # type: ignore

				allowed_inspection_types = ["New Inventory", "Repair", "Maintenance", "QA", "Other"]
				inspection.inspection_type = (
					self.intake_type if self.intake_type in allowed_inspection_types else "Other"  # type: ignore
				)

				# Insert; if legacy schema (Link→Serial No) and no ERP Serial exists, bypass mandatory
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

				frappe.msgprint(_("Instrument Inspection <b>{0}</b> created.").format(inspection.name))

			# --- 5) Clarinet Initial Setup (New Inventory only) ---------------------------------
			if (
				self.intake_type == "New Inventory"  # type: ignore
				and settings.get("auto_create_initial_setup", 1)
				and self.instrument
				and not frappe.db.exists("Clarinet Initial Setup", {"instrument": self.instrument})
			):
				setup = frappe.new_doc("Clarinet Initial Setup")
				setup.instrument = self.instrument  # type: ignore
				setup.intake = self.name  # type: ignore
				setup.setup_date = self.intake_date or nowdate()  # type: ignore
				setup.status = "Open"  # type: ignore
				setup.insert(ignore_permissions=True)
				frappe.msgprint(_("Clarinet Initial Setup <b>{0}</b> created.").format(setup.name))

			# --- 6) Consent Form (Repair/Maintenance, if enabled in settings) -------------------
                        if settings.get("auto_create_consent_form") and self._should_create_consent():
                                self._create_consent_form(settings)

                        self._apply_player_profile_links()

                        # --- Timeline entries ---------------------------------------------------------------
                        add_timeline_entries(self, "after_insert")

		except Exception:
			frappe.log_error(title="ClarinetIntake.after_insert", message=frappe.get_traceback())
			frappe.throw(
				_(
					"An error occurred during automated record creation. "
					"Please check system logs or contact an administrator."
				)
			)

	# ---------------------------------------------------------------------------
	# Internals used by automation
	# ---------------------------------------------------------------------------
	def _compute_inspection_serial_value(
		self, serial_no_input: str, isn_name: str | None
	) -> tuple[str | None, bool]:
		"""
		Compute value for Instrument Inspection.serial_no and whether to bypass mandatory:

		• If Link → Instrument Serial Number (preferred): ensure/return ISN name. (no bypass)
		• If Link → Serial No (legacy): do NOT create ERP Serial No here; return (None, True) if missing. (bypass)
		• If Data: return raw serial. (no bypass)

		Returns: (value_to_set, requires_mandatory_bypass)
		"""
		df = _get_field_df("Instrument Inspection", "serial_no")
		fieldtype = getattr(df, "fieldtype", None) if df else None
		options = getattr(df, "options", None) if df else None

		# Link → Instrument Serial Number (preferred)
		if fieldtype == "Link" and options == "Instrument Serial Number":
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
			return None, True  # signal to bypass mandatory

		# Data field: store raw
		return (serial_no_input or None), False

	def _find_existing_instrument_by_serial(self, serial_no_input: str, isn_name: str | None):
		"""
		Find an Instrument by serial, compatible with both schemas:
		• Link → Instrument Serial Number: search by ISN name.
		• Data: search by raw serial string.
		"""
		field_type = _get_instrument_serial_field_type()

		if field_type == "Link" and isn_name:
			name = frappe.db.get_value("Instrument", {"serial_no": isn_name}, "name")
			return frappe.get_doc("Instrument", name) if name else None  # type: ignore

		# Legacy Data field or no ISN yet — search by plain serial
		name = frappe.db.get_value("Instrument", {"serial_no": serial_no_input}, "name")
		return frappe.get_doc("Instrument", name) if name else None  # type: ignore

	def _should_create_consent(self) -> bool:
		"""
		Determine if consent form should be auto-created based on intake type and settings.
		"""
		consent_types = get_intake_settings().get("consent_required_for_intake_types", "Repair and Maintenance")
		
		if consent_types == "Repair":
			return self.intake_type == "Repair"  # type: ignore
		elif consent_types == "Maintenance":
			return self.intake_type == "Maintenance"  # type: ignore
		else:  # "Repair and Maintenance" or default
			return self.intake_type in ("Repair", "Maintenance")  # type: ignore

	def _create_consent_form(self, settings: dict) -> None:
		"""
		Create a Consent Form linked to this intake (idempotent).
		"""
		template = settings.get("default_consent_template")
		if not template:
			frappe.log_error(
				title="Clarinet Intake: No Consent Template",
				message=f"auto_create_consent_form is enabled but default_consent_template not set in settings for intake {self.name}"
			)
			return

		# Check if consent form already exists for this intake
		existing = frappe.db.exists("Consent Form", {"reference_doctype": "Clarinet Intake", "reference_name": self.name})
		if existing:
			return  # Already created

		try:
			consent = frappe.new_doc("Consent Form")
			consent.consent_template = template  # type: ignore
			consent.reference_doctype = "Clarinet Intake"  # type: ignore
			consent.reference_name = self.name  # type: ignore
			
			# Link customer if available
			if self.customer:  # type: ignore
				consent.customer = self.customer  # type: ignore
			
			# Pre-fill common fields (if Consent Form has these)
			if hasattr(consent, "customer_name") and self.customer_full_name:  # type: ignore
				consent.customer_name = self.customer_full_name  # type: ignore
			if hasattr(consent, "customer_email") and self.customer_email:  # type: ignore
				consent.customer_email = self.customer_email  # type: ignore
			if hasattr(consent, "customer_phone") and self.customer_phone:  # type: ignore
				consent.customer_phone = self.customer_phone  # type: ignore
			
			consent.insert(ignore_permissions=True)
			
			# Link back to intake
			self.db_set("consent_form", consent.name, update_modified=False)
			
			frappe.msgprint(_("Consent Form <b>{0}</b> created and linked.").format(consent.name))
			
		except Exception:
			frappe.log_error(
				title="Clarinet Intake: Consent Form Creation Failed",
				message=frappe.get_traceback()
			)
			# Non-fatal: log but don't fail the intake creation


# ------------------------------------------------------------------------------
# Whitelisted API (server)
# ------------------------------------------------------------------------------
@frappe.whitelist(allow_guest=False)
def get_instrument_by_serial(serial_no: str) -> dict[str, str | int | None] | None:
	"""
	Secure, backwards-compatible fetch of Instrument details by a user-entered serial.
	Resolves against Instrument Serial Number when Instrument.serial_no is Link; otherwise
	falls back to legacy Data matching.

	Returns a dict with key fields or None.
	"""
	if not serial_no:
		return None

	# Basic permission guard on the doctype
	if not frappe.has_permission("Clarinet Intake", ptype="read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	# Prefer ISN path for Link-style Instrument.serial_no
	isn = find_by_serial(serial_no)
	if isn and isn.get("name") and _get_instrument_serial_field_type() == "Link":
		instr_name = frappe.db.get_value("Instrument", {"serial_no": isn["name"]}, "name")
		if instr_name:
			data = frappe.db.get_value(
				"Instrument",
				instr_name,
				[
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
				data["manufacturer"] = data.pop("brand", None)  # normalize key for intake UI
			return data  # type: ignore

	# Legacy Data fallback
	data = frappe.db.get_value(
		"Instrument",
		{"serial_no": serial_no},
		[
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
		data["manufacturer"] = data.pop("brand", None)
	return data  # type: ignore


@frappe.whitelist(allow_guest=False)
def get_instrument_inspection_name(intake_record_id: str) -> str | None:
	"""Return the Instrument Inspection name linked to a given intake, if any."""
	if not intake_record_id:
		return None

	# Permission guard on the doctype
	if not frappe.has_permission("Clarinet Intake", ptype="read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	return frappe.db.get_value(
		"Instrument Inspection", {"intake_record_id": intake_record_id}, "name"
	)  # type: ignore


# ------------------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------------------
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


def _get_field_df(doctype: str, fieldname: str):
	"""Return the DocField for (doctype, fieldname) or None."""
	try:
		return frappe.get_meta(doctype).get_field(fieldname)
	except Exception:
		return None
