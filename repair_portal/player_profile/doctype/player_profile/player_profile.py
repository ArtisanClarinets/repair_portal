# File Header Template
# Relative Path: repair_portal/player_profile/doctype/player_profile/player_profile.py
# Last Updated: 2025-08-14
# Version: v2.1
# Purpose: Core business logic and automation for Player Profile (CRM), covering full musician lifecycle, preferences,
#          marketing, compliance, and CRM triggers. Updates "instruments_owned" sync to display serial intelligently
#          whether stored as raw, ERPNext Serial No, or ISN (Link).
# Dependencies: Customer, Instrument Profile, Sales Invoice, Repair Log, Email Group Member, Frappe/ERPNext APIs,
#               repair_portal.repair_portal.utils.serials (ISN helpers)

from datetime import datetime

import frappe
from frappe.model.document import Document


# ISN resolve (get raw serial from ISN when needed)
def _resolve_serial_display(instrument_profile_row: dict) -> str | None:
	"""
	Returns a human-friendly serial string to display in 'instruments_owned':
	  - If Instrument Profile has 'serial_no' set (string), prefer it.
	  - Else, if Instrument Profile links to an Instrument, fetch Instrument.serial_no:
	       • If it's a Link to ISN, show ISN.serial (raw stamped string).
	       • If it's a Data/ERPNext Serial No, show that value.
	"""
	if instrument_profile_row.get("serial_no"):
		return instrument_profile_row.get("serial_no")

	instrument_name = instrument_profile_row.get("instrument")
	if not instrument_name:
		return None

	# Get Instrument.serial_no value and its field type
	serial_value = frappe.db.get_value("Instrument", instrument_name, "serial_no")
	if not serial_value:
		return None

	# Determine fieldtype dynamically
	try:
		df = frappe.get_meta("Instrument").get_field("serial_no")
		fieldtype = getattr(df, "fieldtype", None) if df else None
	except Exception:
		fieldtype = None

	if fieldtype == "Link" and frappe.db.exists("Instrument Serial Number", serial_value):
		return frappe.db.get_value("Instrument Serial Number", serial_value, "serial")  # type: ignore

	# Legacy Data or ERPNext Serial No docname stored as Data
	return serial_value  # type: ignore


class PlayerProfile(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from repair_portal.customer.doctype.instruments_owned.instruments_owned import (
			InstrumentsOwned,
		)
		from repair_portal.player_profile.doctype.player_equipment_preference.player_equipment_preference import (
			PlayerEquipmentPreference,
		)

		affiliation: DF.Data | None
		communication_preference: DF.Literal["Email", "SMS", "Phone Call"]
		customer_lifetime_value: DF.Currency
		equipment_preferences: DF.Table[PlayerEquipmentPreference]
		g_sharp_a_connection: DF.Data | None
		instruments_owned: DF.Table[InstrumentsOwned]
		intonation_notes: DF.SmallText | None
		key_height_preference: DF.Literal["Low/Close", "Standard", "High/Open"]
		last_visit_date: DF.Date | None
		mailing_address: DF.SmallText | None
		newsletter_subscription: DF.Check
		player_level: DF.Literal[
			"Student (Beginner)",
			"Student (Advanced)",
			"Amateur/Hobbyist",
			"University Student",
			"Professional (Orchestral)",
			"Professional (Jazz/Commercial)",
			"Educator",
			"Collector",
		]  # type: ignore
		player_name: DF.Data
		player_profile_id: DF.Data
		preferred_name: DF.Data | None
		preferred_pad_type: DF.Data | None
		primary_email: DF.Data
		primary_phone: DF.Data | None
		primary_playing_styles: DF.Check
		primary_teacher: DF.Data | None
		profile_creation_date: DF.Date | None
		profile_status: DF.Literal["Draft", "Active", "Archived"]
		referral_source: DF.Data | None
		spring_tension_preference: DF.Literal["Light/Fluid", "Standard/Firm", "Heavy/Resistant"]
		targeted_marketing_optin: DF.Check
		technician_notes: DF.SmallText | None
	# end: auto-generated types
	"""
    Player Profile - Persistent CRM profile for a unique musician/player.
    Handles full identity, musical, equipment, service preferences, analytics, permissions, and CRM automations.
    """

	def autoname(self):
		if not self.player_profile_id or self.player_profile_id == "New":
			self.player_profile_id = f"PLAYER-{frappe.generate_hash(length=5).upper()}"

	def validate(self):
		"""
		Ensures required fields, compliance logic, and triggers downstream CRM actions.
		"""
		# Core field checks
		if not self.player_name:
			frappe.throw("Full Name is required for Player Profile.")
		if not self.primary_email:
			frappe.throw("Primary Email is required for Player Profile.")
		# COPPA/child privacy (if date of birth is present)
		if hasattr(self, "date_of_birth") and self.date_of_birth:  # type: ignore
			try:
				age = (datetime.now().date() - self.date_of_birth).days // 365  # type: ignore
				if age < 13:
					self._block_marketing_emails()
			except Exception:
				frappe.log_error(frappe.get_traceback(), "PlayerProfile.validate failed on DOB")

		# CRM triggers (opt-ins)
		if self.newsletter_subscription:
			self._sync_email_group()

		# Auto-set creation date if not set
		if not self.profile_creation_date:
			self.profile_creation_date = frappe.utils.today()  # type: ignore

		# Sync owned instruments list (links)
		self._sync_instruments_owned()
		self._calc_lifetime_value()

	def _block_marketing_emails(self):
		"""
		Unsubscribes user if under 13, notifies parent/guardian.
		"""
		try:
			if self.primary_email:
				frappe.db.set_value("Email Group Member", {"email": self.primary_email}, "unsubscribed", 1)
			# Notify parent/client user if available
			customer = frappe.db.get_value(
				"Customer", {"email_id": self.primary_email}, ["linked_user"], as_dict=True
			)  # type: ignore
			if customer and customer.linked_user:  # type: ignore
				parent_email = frappe.db.get_value("User", customer.linked_user, "email")  # type: ignore
				if parent_email:
					subject = f"Profile Marketing Blocked for {self.player_name}"
					message = (
						f"Dear Parent/Guardian,<br>Due to compliance, marketing emails for {self.player_name} "
						f"have been blocked (age under 13). No action is required.<br>Thank you!<br>— The Artisan Clarinets Team"
					)
					frappe.sendmail(recipients=[parent_email], subject=subject, message=message)
		except Exception:
			frappe.log_error(
				frappe.get_traceback(), "PlayerProfile: block_marketing_emails notification failed"
			)

	def _sync_email_group(self):
		"""
		Syncs the player to newsletter or marketing groups if opted-in.
		"""
		try:
			if self.primary_email:
				frappe.get_doc(
					{
						"doctype": "Email Group Member",
						"email": self.primary_email,
						"email_group": "Player Newsletter",
					}
				).insert(ignore_permissions=True, ignore_if_duplicate=True)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "PlayerProfile: sync_email_group failed")

	def _sync_instruments_owned(self):
		"""
		Updates the instruments_owned child table from linked Instrument Profile docs.
		ISN-aware: displays human serial even when Instrument holds a Link to ISN.
		"""
		try:
			owned = frappe.get_all(
				"Instrument Profile",
				filters={"owner_player": self.name},
				fields=[
					"name",
					"serial_no",
					"model",
					"instrument",
				],  # include instrument link for ISN-aware resolution
			)
			self.set("instruments_owned", [])
			for row in owned:
				serial_display = _resolve_serial_display(row)
				self.append(
					"instruments_owned",
					{"name": row["name"], "serial_no": serial_display, "model": row.get("model")},
				)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "PlayerProfile: sync_instruments_owned failed")

	def _calc_lifetime_value(self):
		"""
		Calculates Customer Lifetime Value based on linked Sales Invoices.
		"""
		try:
			invoices = frappe.get_all(
				"Sales Invoice",
				filters={"player_profile": self.name, "docstatus": 1},
				fields=["grand_total"],
			)
			self.customer_lifetime_value = sum(inv["grand_total"] for inv in invoices) if invoices else 0
		except Exception:
			frappe.log_error(frappe.get_traceback(), "PlayerProfile: calc_lifetime_value failed")

	def on_update(self):
		"""
		Called on every save; handles CRM triggers (like/notify), analytics, and logging.
		"""
		try:
			# CRM Notification Example: If a "liked" instrument is available, trigger notification
			for liked in self.get("instruments_liked") or []:
				instrument = frappe.get_doc("Instrument Profile", liked.instrument)
				if instrument.status == "Available":  # type: ignore
					self._notify_liked_instrument(instrument)
			# Staff Notes handling (running log)
			# No duplicate notes; always log new note if present
		except Exception:
			frappe.log_error(frappe.get_traceback(), "PlayerProfile: on_update CRM triggers failed")

	def _notify_liked_instrument(self, instrument):
		"""
		Notifies the player when a liked instrument becomes available.
		"""
		try:
			if self.primary_email:
				subject = f"Your Liked Instrument {instrument.name} is Now Available!"
				message = (
					f"Hi {self.preferred_name or self.player_name},<br><br>"
					f"Your liked instrument <b>{instrument.name}</b> is now in stock! "
					f"<a href='/app/instrument-profile/{instrument.name}'>View Details</a>."
					f"<br><br>— The Artisan Clarinets Team"
				)
				frappe.sendmail(recipients=[self.primary_email], subject=subject, message=message)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "PlayerProfile: notify_liked_instrument failed")
